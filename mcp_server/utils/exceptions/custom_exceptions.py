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


class DatabaseConnectionException(AppBaseException):
    def __init__(self, detail: str = "Failed to connect to the database."):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.DB_CONNECTION_FAILED, "BB_DB_001"),
            message=detail,
            status_code=settings.http_service_unavailable,
        )


class MenuItemNotFoundException(AppBaseException):
    def __init__(self, item_name: str):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.MENU_ITEM_NOT_FOUND, "BB_MENU_001"),
            message=f"Menu item '{item_name}' not found.",
            status_code=settings.http_not_found,
        )


class OrderNotFoundException(AppBaseException):
    def __init__(self, order_id: str):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.ORDER_NOT_FOUND, "BB_ORD_001"),
            message=f"Order '{order_id}' not found.",
            status_code=settings.http_not_found,
        )


class InsufficientStockException(AppBaseException):
    def __init__(self, item_name: str, available: int):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.INSUFFICIENT_STOCK, "BB_ORD_002"),
            message=f"Insufficient stock for '{item_name}'. Available: {available}.",
            status_code=settings.http_bad_request,
        )


class InvalidRequestException(AppBaseException):
    def __init__(self, detail: str = "Invalid request."):
        super().__init__(
            error_code=ErrorCodeStatus.get(ErrorCode.INVALID_REQUEST, "BB_REQ_001"),
            message=detail,
            status_code=settings.http_bad_request,
        )
