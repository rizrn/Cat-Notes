from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.llm import QuizQuestion


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)
    author: str = Field(min_length=1, max_length=200)


class NoteUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    author: str | None = Field(default=None, min_length=1, max_length=200)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    author: str
    created_at: datetime


class SummaryRead(BaseModel):
    note_id: int
    summary: str


class QuizRead(BaseModel):
    note_id: int
    questions: list[QuizQuestion]


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=500)


class AskSource(BaseModel):
    note_id: int
    title: str
    excerpt: str


class AskRead(BaseModel):
    answer: str
    sources: list[AskSource]
