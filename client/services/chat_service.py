import logging
from typing import Optional

from models.schemas import ChatRequest, ChatResponse, OrderDetails, PendingApproval
from agent.mcp_client import run_agent, stream_agent, run_structured_agent, resume_agent, has_pending_interrupt
from utils.exceptions.custom_exceptions import AppBaseException, InvalidRequestException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from settings import settings

logger = logging.getLogger(__name__)

class ChatService:

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        try:
            mode = request.mode.lower().strip()
            logger.info(f"[CHAT] thread={request.thread_id} mode={mode} stream={request.stream}")


            if mode == "structured":
                return await self.process_structured(request)

            if request.stream:
                chunks = await stream_agent(
                    request.message,
                    thread_id=request.thread_id,
                )
                return ChatResponse(
                    message="".join(chunks),
                    stream_chunks=chunks,
                )

            if await has_pending_interrupt(request.thread_id):
                logger.info(f"[HITL] Pending interrupt found for thread={request.thread_id}")
                logger.info(f"[HITL] Decision received: '{request.message}' thread={request.thread_id}")
                return await self.process_hitl_decision(request.thread_id, request.message)

            message, pending = await run_agent(
                request.message,
                thread_id=request.thread_id,
            )
            
            if pending:
                logger.info(f"[HITL] Interrupt raised for thread={request.thread_id}")
                return ChatResponse(
                    message=(
                        f"Your order is ready to place: "
                        f"{pending['args'].get('items', [])} for "
                        f"{pending['args'].get('customer_name', 'Guest')}. "
                        f"Reply 'approve' to confirm or 'reject' to cancel."
                    ),
                    pending_approval=PendingApproval(
                        tool=pending["tool"],
                        args=pending["args"],
                        description=pending["description"],
                    ),
                )

            return ChatResponse(message=message)
        except AppBaseException:
            raise
        except Exception as exc:
            raise AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.CHAT_PROCESSING_FAILED, "BB_CHAT_001"),
                message=f"Chat processing failed: {str(exc)}",
                status_code=settings.http_internal_server_error,
            )

    async def process_hitl_decision(self, thread_id: str, decision: str) -> ChatResponse:
        try:
            logger.info(f"[HITL] Resuming thread={thread_id} with decision='{decision}'")
            message = await resume_agent(decision=decision, thread_id=thread_id)
            logger.info(f"[HITL] Resume completed for thread={thread_id}")
            return ChatResponse(message=message)
        except AppBaseException:
            raise
        except Exception as exc:
            raise AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.CHAT_PROCESSING_FAILED, "BB_CHAT_001"),
                message=f"Failed to process approval decision: {str(exc)}",
                status_code=settings.http_internal_server_error,
            )

    async def process_structured(self, request: ChatRequest) -> ChatResponse:
        try:
            result = await run_structured_agent(
                request.message,
                OrderDetails,
                thread_id=request.thread_id,
            )

            structured = result.get("structured_response")
            if structured is None:
                raise InvalidRequestException("No structured output returned.")

            if isinstance(structured, OrderDetails):
                structured_output: Optional[OrderDetails] = structured
            else:
                structured_output = OrderDetails(**structured)

            final_message = "Structured output generated."
            if result.get("messages"):
                final_message = result["messages"][-1].content or final_message

            return ChatResponse(
                message=final_message,
                structured_output=structured_output,
            )
        except AppBaseException:
            raise
        except Exception as exc:
            raise AppBaseException(
                error_code=ErrorCodeStatus.get(ErrorCode.CHAT_STRUCTURED_FAILED, "BB_CHAT_002"),
                message=f"Structured chat processing failed: {str(exc)}",
                status_code=settings.http_internal_server_error,
            )
