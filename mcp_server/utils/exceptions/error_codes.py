class ErrorCode:
    DB_CONNECTION_FAILED = "DatabaseConnectionFailedErrorCode"
    INTERNAL_SERVER_ERROR = "InternalServerErrorCode"
    MENU_ITEM_NOT_FOUND = "MenuItemNotFoundErrorCode"
    ORDER_NOT_FOUND = "OrderNotFoundErrorCode"
    INSUFFICIENT_STOCK = "InsufficientStockErrorCode"
    INVALID_REQUEST = "InvalidRequestErrorCode"


ErrorCodeStatus = {
    ErrorCode.DB_CONNECTION_FAILED: "BB_DB_001",
    ErrorCode.INTERNAL_SERVER_ERROR: "BB_SYS_001",
    ErrorCode.MENU_ITEM_NOT_FOUND: "BB_MENU_001",
    ErrorCode.ORDER_NOT_FOUND: "BB_ORD_001",
    ErrorCode.INSUFFICIENT_STOCK: "BB_ORD_002",
    ErrorCode.INVALID_REQUEST: "BB_REQ_001",
}
