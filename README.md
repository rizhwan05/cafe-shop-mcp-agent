# Cafe Shop MCP Agent (MCP architecture)

## Overview
This represents a mature state of the Cafe Shop Model Context Protocol (MCP) setup. It includes a complete setup with the `client` and `mcp_server`, fully utilizing MCP tools, resources, and prompts.

## Project Structure
- **client/**: Manages the user-facing chat and routes, connecting to the MCP Server.
- **mcp_server/**: Provides the domain-specific business logic (coffee shop orders, database), exposed via MCP.

## Tech Stack
- Python 3.11+
- FastAPI
- Model Context Protocol (MCP)
- SQLAlchemy
