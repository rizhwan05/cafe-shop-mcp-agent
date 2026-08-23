# Cafe Shop MCP Agent - Exhaustive Documentation

## System Overview
The **Cafe Shop MCP Agent** ("Bean & Brew") is an advanced implementation of the **Model Context Protocol (MCP)** ecosystem. It consists of two standalone services that communicate securely using the MCP `streamable-http` transport protocol.

The system uses a LangChain-based ReAct agent running on AWS Bedrock to process natural language coffee shop requests, querying live inventory and executing orders against a PostgreSQL database through the MCP server.

---

## 1. Architecture Deep-Dive

### 1.1 The Client Interface (`client/`)
The Client acts as the user-facing API and the LangChain Agent execution environment.
- **Framework**: FastAPI
- **Agent Orchestrator**: LangGraph + LangChain (`create_agent`)
- **LLM Engine**: AWS Bedrock (`ChatBedrock`)
- **Persistence**: LangGraph AsyncPostgresSaver (Checkpointer) for thread-level memory.
- **Middleware Integration**:
  - `SummarizationMiddleware`: Compresses history beyond 2000 tokens or 10 messages.
  - `PIIMiddleware`: Redacts emails, masks credit cards, and redacts phone numbers before sending to Bedrock.
  - `HumanInTheLoopMiddleware`: Intercepts the `add_order` tool call for explicit human approval before execution.

### 1.2 The MCP Server (`mcp_server/`)
The Server exposes domain logic and data boundaries securely.
- **Framework**: FastMCP (`mcp.server.fastmcp`)
- **Database**: PostgreSQL (managed via SQLAlchemy ORM).
- **Transport**: HTTP SSE (`streamable-http`).

---

## 2. API Contract & Data Flow

### 2.1 Chat Endpoint (Client)
**`POST /api/v1/chat`**

**Request Payload (`ChatRequest`):**
```json
{
  "message": "I'd like to order 2 Cappuccinos please.",
  "mode": "normal", 
  "stream": false,
  "thread_id": "user-session-id"
}
```
*Note: `mode` can be `normal`, `structured`, or left empty. `stream` dictates whether response is SSE or synchronous JSON.*

**Response Payload (`ChatResponse` - Normal Mode):**
```json
{
  "message": "I have set up your order for 2 Cappuccinos. Before I finalize it, do you approve?",
  "structured_output": null,
  "stream_chunks": null,
  "pending_approval": {
    "tool": "add_order",
    "args": {"customer_name": "Guest", "items": [{"item_name": "Cappuccino", "quantity": 2}]},
    "description": "Tool add_order requires approval."
  }
}
```
*(If `pending_approval` is present, the next request's `message` must be exactly "approve" or "reject" with the same `thread_id`).*

### 2.2 Database Schema (MCP Server)
The PostgreSQL database consists of 4 main tables:
1. **`menu_items`**: `menu_item_id` (PK), `name` (unique), `price` (Numeric), `stock_quantity` (int), `is_active` (bool).
2. **`orders`**: `order_id` (UUID PK), `order_sequence_id` (BigInt Seq), `customer_name` (str), `status` (str).
3. **`order_items`**: Junction table linking `orders` and `menu_items` with a `quantity` column.
4. **`error_logs`**: `log_id`, `error_code`, `message`, `source`.

---

## 3. Model Context Protocol (MCP) Bindings

The FastMCP server explicitly registers the following components. The Client loads these unconditionally during session initialization (`load_session_context`).

### 3.1 Tools (`@mcp.tool()`)
| Tool Name | Arguments | Returns | Description |
|-----------|-----------|---------|-------------|
| `check_menu` | *None* | `Dict[str, List[Dict]]` | Fetches active menu items (`name`, `price`, `description`) and current `stock_quantity`. |
| `check_order_status` | `order_sequence_id` (int) | `Dict` | Returns order status (`PENDING`, `PROCESSED`) by looking up the integer sequence ID. |
| `add_order` | `customer_name` (str), `items` (List) | `Dict` | Places order, generates sequence ID, and reduces inventory `stock_quantity`. Intercepted by HITL on the client side. |

### 3.2 Prompts (`@mcp.prompt()`)
- **`brew_buddy_system`**: The primary ReAct agent instructions formatting role, objectives, constraints, and output format (using XML tags `<role>`, `<instructions>`).
- **`order_confirmation(customer_name, items)`**: Generates a warm, formatted confirmation receipt.

### 3.3 Resources (`@mcp.resource()`)
- **`menu://items`**: Read-only text dump of the live menu and prices.
- **`store://info`**: Static string containing store hours, location, and contact policies.

---

## 4. Setup and Execution Steps

### 4.1 Prerequisites
- PostgreSQL running locally or via Docker.
- AWS Bedrock access (AWS credentials configured).
- Python 3.11+ and `uv` package manager.

### 4.2 Start the MCP Server
Navigate to `mcp_server/`, update your `.env` with `DB_HOST`, `DB_USER`, `DB_PASS`, etc., and run:
```bash
uv sync
python main.py
```
*This automatically triggers database migrations (`create_tables.py`) and seeds the default coffee menu, starting FastMCP on port 8000.*

### 4.3 Start the Client API
Navigate to `client/`, update your `.env` with AWS and MCP Server credentials (`MCP_SERVER_URL=http://localhost:8000`), and run:
```bash
uv sync
python main.py
```
*This starts the user-facing FastAPI application on port 8080.*

### 4.4 Example Workflow
1. **User asks for menu:** `POST /api/v1/chat` -> Agent reads `menu://items` resource.
2. **User places order:** `POST /api/v1/chat` -> Agent calls `add_order`. HITL middleware interrupts and returns `pending_approval`.
3. **User approves:** `POST /api/v1/chat` (message: "approve", same thread_id) -> Client resumes LangGraph checkpointer state -> Tool executes on MCP Server -> DB stock reduced.
