from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from functools import lru_cache
from settings import settings


class Database:
    def __init__(self):
        conn_str = (
            f"postgresql+psycopg2://{settings.db_username}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        self.engine = create_engine(conn_str)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )
        print(f"[Singleton] Database engine created - id: {id(self.engine)}")


@lru_cache(maxsize=None)
def get_database() -> Database:
    return Database()


db = get_database()
engine = db.engine
SessionLocal = db.SessionLocal
Base = declarative_base()


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
