from fastapi import FastAPI

from app.middleware import add_process_time, add_request_id
from app.routers.notes import router as notes_router

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

app = FastAPI()
app.include_router(notes_router)

app.middleware("http")(add_process_time)
app.middleware("http")(add_request_id)