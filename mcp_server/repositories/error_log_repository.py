from typing import Optional

from repositories.database import get_db
from repositories.schema.schema import ErrorLogSchema
from utils.exceptions.custom_exceptions import DatabaseConnectionException


class ErrorLogRepository:

    def create_error_log(
        self,
        error_code: str,
        message: str,
        source: str,
        details: Optional[str] = None,
        created_by: str = "system",
    ) -> ErrorLogSchema:
        try:
            with get_db() as session:
                record = ErrorLogSchema(
                    error_code=error_code,
                    message=message,
                    source=source,
                    details=details,
                    created_by=created_by,
                    updated_by=created_by,
                )
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)
                return record
        except Exception as exc:
            raise DatabaseConnectionException(detail=f"Failed to log error: {str(exc)}")
