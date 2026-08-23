from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, PIIMiddleware, HumanInTheLoopMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from settings import settings
from utils.helpers import get_llm
from utils.exceptions.custom_exceptions import AppBaseException, InvalidRequestException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
import logging

logger = logging.getLogger(__name__)

def get_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "bean-brew-tools": {
                "transport": "streamable_http",
                "url": settings.mcp_server_url,
            }
        }
    )


def get_db_uri() -> str:
    encoded_password = quote_plus(settings.db_password)
    return (
        f"postgresql://{settings.db_username}:{encoded_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


def get_pii_middleware() -> list:
    return [
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ]


def get_summarization_middleware() -> SummarizationMiddleware:
    summary_llm = get_llm(
        max_tokens=settings.summary_max_tokens,
        temperature=0,
    )
    return SummarizationMiddleware(
        model=summary_llm,
        trigger=[
            ("tokens", 2000),
            ("messages", 10),
        ],
        keep=("messages", settings.summary_keep_messages),
        trim_tokens_to_summarize=None,
    )


def get_hitl_middleware() -> HumanInTheLoopMiddleware:
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "add_order": {
                "allowed_decisions": ["approve", "reject"],
            },
            "check_menu": False,
            "check_order_status": False,
        },
        description_prefix="Order placement requires your approval",
    )


async def load_session_context(session) -> tuple:
    tools = await load_mcp_tools(session)

    prompt_messages = await load_mcp_prompt(
        session,
        "brew_buddy_system",
        arguments={},
    )

    system_text = "\n".join(
        m.content for m in prompt_messages if hasattr(m, "content") and m.content
    )

    blobs = await load_mcp_resources(session)
    resource_context = ""
    for blob in blobs:
        try:
            uri = blob.metadata.get("uri", "")
            text = blob.as_bytes().decode("utf-8", errors="replace")
            resource_context += f"\n[{uri}]\n{text}\n"
        except Exception:
            continue

    if resource_context:
        system_text += f"\n\nHere is the available context:\n{resource_context}"

    return tools, system_text


def extract_pending_approval(result: Any) -> Optional[Dict]:
    interrupts = result.get("__interrupt__")
    if not interrupts:
        return None

    interrupt = interrupts[0]
    
    value = interrupt.value if hasattr(interrupt, "value") else {}
    
    action_requests = value.get("action_requests", [])
    
    if not action_requests:
        return None

    first_action = action_requests[0] 

    return {
        "tool": first_action.get("name", "add_order"),
        "args": first_action.get("args", {}),
        "description": value.get("description", "Order placement requires your approval"),
    }


async def has_pending_interrupt(thread_id: str) -> bool:
    async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
        await checkpointer.setup()
        state = await checkpointer.aget({"configurable": {"thread_id": thread_id}})
        if not state:
            logger.info(f"[INTERRUPT CHECK] thread={thread_id} no saved state found")
            return False
        result = bool(state.get("__interrupt__"))
        logger.info(f"[INTERRUPT CHECK] thread={thread_id} pending={result}")
        return result


async def run_agent(message: str, thread_id: str = "default") -> tuple:
    try:
        client = get_client()

        async with client.session("bean-brew-tools") as session:
            tools, system_text = await load_session_context(session)

            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()

                agent = create_agent(
                    model=get_llm(
                        max_tokens=settings.max_tokens,
                        temperature=settings.temperature,
                    ),
                    system_prompt=SystemMessage(content=system_text),
                    tools=tools,
                    middleware=get_pii_middleware() + [get_summarization_middleware(), get_hitl_middleware()],
                    checkpointer=checkpointer,
                )

                config = RunnableConfig(
                    configurable={"thread_id": thread_id}
                )

                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=message)]},
                    config,
                )

                pending = extract_pending_approval(result)
                logger.info(f"[RUN AGENT] thread={thread_id} interrupt_pending={pending is not None}")
                if pending:
                    return None, pending

                return result["messages"][-1].content, None

    except AppBaseException:
        raise
    except Exception as exc:
        logger.error(f"[RUN AGENT] thread={thread_id} failed: {str(exc)}")
        raise AppBaseException(
            error_code=ErrorCodeStatus.get(ErrorCode.MCP_AGENT_INVOKE_FAILED, "BB_MCP_002"),
            message=f"Agent invocation failed: {str(exc)}",
            status_code=settings.http_internal_server_error,
        )


async def resume_agent(decision: str, thread_id: str) -> str:
    try:
        logger.info(f"[RESUME] thread={thread_id} decision='{decision}'")
        client = get_client()

        async with client.session("bean-brew-tools") as session:
            tools, system_text = await load_session_context(session)

            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()

                agent = create_agent(
                    model=get_llm(
                        max_tokens=settings.max_tokens,
                        temperature=settings.temperature,
                    ),
                    system_prompt=SystemMessage(content=system_text),
                    tools=tools,
                    middleware=get_pii_middleware() + [get_summarization_middleware(), get_hitl_middleware()],
                    checkpointer=checkpointer,
                )

                config = RunnableConfig(
                    configurable={"thread_id": thread_id}
                )

                result = await agent.ainvoke(
                    Command(resume={
                        "decisions": [{
                            "type": decision
                        }]
                    }),
                    config,
                )

                logger.info(f"[RESUME] Completed for thread={thread_id}")
                return result["messages"][-1].content

    except AppBaseException:
        raise
    except Exception as exc:
        logger.error(f"[RESUME] thread={thread_id} failed: {str(exc)}")
        raise AppBaseException(
            error_code=ErrorCodeStatus.get(ErrorCode.MCP_AGENT_INVOKE_FAILED, "BB_MCP_002"),
            message=f"Agent resume failed: {str(exc)}",
            status_code=settings.http_internal_server_error,
        )


async def stream_agent(message: str, thread_id: str = "default") -> List[str]:
    try:
        client = get_client()

        async with client.session("bean-brew-tools") as session:
            tools, system_text = await load_session_context(session)

            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()

                agent = create_agent(
                    model=get_llm(
                        max_tokens=settings.max_tokens,
                        temperature=settings.temperature,
                    ),
                    system_prompt=SystemMessage(content=system_text),
                    tools=tools,
                    middleware=get_pii_middleware() + [get_summarization_middleware(), get_hitl_middleware()],
                    checkpointer=checkpointer,
                )

                config = RunnableConfig(
                    configurable={"thread_id": thread_id}
                )

                print("\n[Brew Buddy Streaming] ", end="", flush=True)

                chunks: List[str] = []
                async for chunk in agent.astream(
                    {"messages": [HumanMessage(content=message)]},
                    config,
                    stream_mode="messages",
                ):
                    msg, metadata = chunk
                    if isinstance(msg, AIMessage) and msg.content:
                        content = msg.content
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and "text" in block:
                                    print(block["text"], end="", flush=True)
                                    chunks.append(block["text"])
                        elif isinstance(content, str):
                            print(content, end="", flush=True)
                            chunks.append(content)

                print("\n[Stream End]", flush=True)
                return chunks

    except AppBaseException:
        raise
    except Exception as exc:
        raise AppBaseException(
            error_code=ErrorCodeStatus.get(ErrorCode.MCP_STREAM_FAILED, "BB_MCP_003"),
            message=f"Streaming agent failed: {str(exc)}",
            status_code=settings.http_internal_server_error,
        )


async def run_structured_agent(
    message: str,
    response_format,
    thread_id: str = "default",
) -> dict:
    try:
        client = get_client()

        async with client.session("bean-brew-tools") as session:
            tools, system_text = await load_session_context(session)

            async with AsyncPostgresSaver.from_conn_string(get_db_uri()) as checkpointer:
                await checkpointer.setup()

                agent = create_agent(
                    model=get_llm(max_tokens=settings.max_tokens, temperature=0),
                    system_prompt=SystemMessage(content=system_text),
                    tools=tools,
                    middleware=get_pii_middleware() + [get_summarization_middleware(), get_hitl_middleware()],
                    response_format=ToolStrategy(response_format),
                    checkpointer=checkpointer,
                )

                config = RunnableConfig(
                    configurable={"thread_id": thread_id}
                )

                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=message)]},
                    config,
                )

                structured = result.get("structured_response")
                if structured is None:
                    raise InvalidRequestException("No structured output returned.")

                if isinstance(structured, response_format):
                    structured_output = structured
                else:
                    structured_output = response_format(**structured)

                if not structured_output.items:
                    raise InvalidRequestException(
                        "Requested item is not on our menu. Please check the menu and try again."
                    )

                if not structured_output.customer_name:
                    structured_output.customer_name = "Guest"

                result["structured_response"] = structured_output
                return result

    except AppBaseException:
        raise
    except Exception as exc:
        raise AppBaseException(
            error_code=ErrorCodeStatus.get(ErrorCode.MCP_AGENT_INVOKE_FAILED, "BB_MCP_002"),
            message=f"Structured agent failed: {str(exc)}",
            status_code=settings.http_internal_server_error,
        )
