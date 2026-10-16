import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import add_process_time, add_request_id, log_requests
from app.routers.notes import router as notes_router

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = FastAPI()
app.include_router(notes_router)

app.middleware("http")(add_process_time)
app.middleware("http")(log_requests)
app.middleware("http")(add_request_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)