import boto3
from langchain_aws import ChatBedrock
from settings import settings
from utils.exceptions.custom_exceptions import AppBaseException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus


def get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.aws_region,
    )


def get_llm(max_tokens: int = None, temperature: float = None) -> ChatBedrock:
    if not settings.model_id:
        raise AppBaseException(
            error_code=ErrorCodeStatus.get(ErrorCode.INTERNAL_SERVER_ERROR, "BB_SYS_001"),
            message="MODEL_ID is required for Bedrock.",
            status_code=settings.http_internal_server_error,
        )
    return ChatBedrock(
        client=get_bedrock_client(),
        model_id=settings.model_id,
        provider=settings.provider,
        model_kwargs={
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature if temperature is not None else settings.temperature,
        },
    )
