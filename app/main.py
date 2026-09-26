from fastapi import FastAPI

from app.routers.notes import router as notes_router

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

app = FastAPI()
app.include_router(notes_router)
