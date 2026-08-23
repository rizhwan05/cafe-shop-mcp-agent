from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from settings import settings


class AppBaseException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message
        }


class InvalidRequestException(AppBaseException):
    def __init__(self, detail: str = "Invalid request."):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.INVALID_REQUEST, "BB_REQ_001"),
            message=detail,
            status_code=settings.http_bad_request,
        )
