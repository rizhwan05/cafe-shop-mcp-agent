import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_name = os.getenv("DB_NAME", "bean_brew_db")
        self.db_username = os.getenv("DB_USERNAME", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "Admin123")

        self.mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
        self.mcp_port = int(os.getenv("MCP_PORT", "8000"))

        # HTTP status codes
        self.http_ok = 200
        self.http_created = 201
        self.http_bad_request = 400
        self.http_not_found = 404
        self.http_internal_server_error = 500
        self.http_service_unavailable = 503


settings = Settings()
