import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from migrations.create_tables import create_tables
from router.router import get_mcp
from settings import settings

if __name__ == "__main__":
    try:
        print("Creating tables and seeding data...")
        create_tables()
        print("Tables ready.")

        mcp = get_mcp()

        print(f"Starting MCP Server at http://{settings.mcp_host}:{settings.mcp_port}/mcp")
        mcp.run(transport="streamable-http")
    except Exception as exc:
        raise RuntimeError(f"MCP server startup failed: {str(exc)}") from exc
