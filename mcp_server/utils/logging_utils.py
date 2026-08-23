from typing import Optional

from repositories.error_log_repository import ErrorLogRepository
from utils.exceptions.custom_exceptions import AppBaseException


def log_and_raise(exc: AppBaseException, source: str, details: Optional[str] = None) -> None:
    try:
        repo = ErrorLogRepository()
        repo.create_error_log(
            error_code=exc.error_code,
            message=exc.message,
            source=source,
            details=details,
        )
    except Exception:
        pass
    raise exc
