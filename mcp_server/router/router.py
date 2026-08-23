from tools.mcp_tools import mcp
from prompts.system_prompt import register_prompts
from resources.resources import register_resources

try:
    register_prompts(mcp)
except Exception as exc:
    raise RuntimeError(f"Failed to register MCP prompts: {str(exc)}") from exc

try:
    register_resources(mcp)
except Exception as exc:
    raise RuntimeError(f"Failed to register MCP resources: {str(exc)}") from exc


def get_mcp():
    return mcp
