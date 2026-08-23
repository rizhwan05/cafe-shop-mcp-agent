import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.port = int(os.getenv("PORT", "8080"))
        self.host = os.getenv("HOST", "0.0.0.0")
        self.log_level = os.getenv("LOG_LEVEL", "info")

        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("MODEL_ID", "")
        self.provider = os.getenv("MODEL_PROVIDER", "amazon")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.3"))

        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")

        # Database — used by AsyncPostgresSaver checkpointer
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "bean_brew_db")
        self.db_username = os.getenv("DB_USERNAME", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "Admin123")

        # Summarization middleware
        self.summary_max_tokens = int(os.getenv("SUMMARY_MAX_TOKENS", "300"))
        self.summary_keep_messages = int(os.getenv("SUMMARY_KEEP_MESSAGES", "4"))

        # HTTP status codes
        self.http_ok = 200
        self.http_created = 201
        self.http_bad_request = 400
        self.http_not_found = 404
        self.http_internal_server_error = 500
        self.http_service_unavailable = 503


settings = Settings()
