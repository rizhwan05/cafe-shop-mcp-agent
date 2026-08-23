# Cafe Shop MCP Agent (MCP architecture)

## Overview
This repository implements a full **Model Context Protocol (MCP)** ecosystem for a fictitious "Bean & Brew" Cafe Shop. It demonstrates how to expose domain-specific business logic (coffee shop orders, inventory) via an MCP server, and how to build a client that connects to it.

## Architecture
The project is split into two distinct services:
1. **Client API (`client/`)**: A FastAPI application that serves as the user-facing interface. It accepts user chat requests and routes them to the MCP Server.
2. **MCP Server (`mcp_server/`)**: A backend service exposing tools, resources, and prompts over the MCP protocol (using `streamable-http`). It uses **SQLAlchemy** to connect to an underlying SQL database.

## Application Flow
1. **User Request**: A user sends a message to the Client API endpoint (`/api/v1/chat`).
2. **Client Processing**: The `ChatService` in the client interprets the request and communicates with the MCP Server to discover available tools (e.g., `create_order`, `check_inventory`).
3. **MCP Server Execution**: The MCP Server receives the standardized tool execution request, queries/mutates the SQLAlchemy database, and returns the context or result.
4. **Response**: The Client wraps the MCP result in a structured response and returns it to the user.

## Endpoints

### Client API
- `POST /api/v1/chat`
  - **Payload**: JSON containing `thread_id`, `mode`, and the user's message.
  - **Description**: The primary entry point for user interactions. Routes the chat through the MCP protocol.

### MCP Server
- Exposes standard Model Context Protocol (MCP) endpoints via HTTP SSE or `streamable-http` at `/mcp`.

## Usage Steps

### 1. Setup the MCP Server
```bash
cd mcp_server
uv sync
python main.py
```
*(This will automatically run `create_tables()` to seed the database and start the server on its designated port).*

### 2. Setup the Client API
In a new terminal window:
```bash
cd client
uv sync
python main.py
```
*(This starts the user-facing FastAPI server, usually on `127.0.0.1:8000`).*

### 3. Test the Flow
Send a POST request to `http://127.0.0.1:8000/api/v1/chat` asking to "Order a latte".
