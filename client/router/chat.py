from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.schemas import ChatRequest, ChatResponse
from services.chat_service import ChatService
from utils.exceptions.custom_exceptions import AppBaseException
from settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"[REQUEST] thread={request.thread_id} mode={request.mode} stream={request.stream}")
    try:
        service = ChatService()
        response: ChatResponse = await service.process_chat(request)
        logger.info(f"[RESPONSE] thread={request.thread_id} status=200")
        return JSONResponse(
            content=response.model_dump(exclude_none=True),
            status_code=settings.http_ok,
        )
    except AppBaseException as e:
        logger.error(f"[ERROR] thread={request.thread_id} error_code={e.error_code} message={e.message}")
        return JSONResponse(
            content={"error_code": e.error_code, "message": e.message},
            status_code=e.status_code,
        )
    except Exception as e:
        logger.error(f"[ERROR] thread={request.thread_id} unexpected error: {str(e)}")
        return JSONResponse(
            content={"error_code": "BB_SYS_001", "message": str(e)},
            status_code=settings.http_internal_server_error,
        )
