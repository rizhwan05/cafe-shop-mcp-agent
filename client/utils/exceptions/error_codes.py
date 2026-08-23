class ErrorCode:
    INTERNAL_SERVER_ERROR = "InternalServerErrorCode"
    CHAT_PROCESSING_FAILED = "ChatProcessingFailedErrorCode"
    CHAT_STRUCTURED_FAILED = "ChatStructuredFailedErrorCode"
    MCP_TOOLS_LOAD_FAILED = "McpToolsLoadFailedErrorCode"
    MCP_AGENT_INVOKE_FAILED = "McpAgentInvokeFailedErrorCode"
    MCP_STREAM_FAILED = "McpStreamFailedErrorCode"
    INVALID_REQUEST = "InvalidRequestErrorCode"


ErrorCodeStatus = {
    ErrorCode.INTERNAL_SERVER_ERROR: "BB_SYS_001",
    ErrorCode.CHAT_PROCESSING_FAILED: "BB_CHAT_001",
    ErrorCode.CHAT_STRUCTURED_FAILED: "BB_CHAT_002",
    ErrorCode.MCP_TOOLS_LOAD_FAILED: "BB_MCP_001",
    ErrorCode.MCP_AGENT_INVOKE_FAILED: "BB_MCP_002",
    ErrorCode.MCP_STREAM_FAILED: "BB_MCP_003",
    ErrorCode.INVALID_REQUEST: "BB_REQ_001",
}
