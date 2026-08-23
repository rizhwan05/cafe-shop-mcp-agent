import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from router.chat import router as chat_router
from utils.exceptions.custom_exceptions import AppBaseException
from settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Bean & Brew Client API...")
    yield
    print("Shutting down Bean & Brew Client API...")


app = FastAPI(title="Bean & Brew Client API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=settings.http_internal_server_error,
        content={"error_code": "BB_SYS_001", "message": "An unexpected error occurred."}
    )


app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level
    )
