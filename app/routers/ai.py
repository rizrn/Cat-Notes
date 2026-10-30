from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_api_key
from app.database import DbSession
from app.models import Note
from app.schemas import AskRead, AskRequest, QuizRead, SummaryRead
from app.services.llm import generate_quiz, summarize
from app.services.rag import answer_from_notes

router = APIRouter(tags=["ai"], dependencies=[Depends(require_api_key)])


@router.post(
    "/notes/{note_id}/summary",
    response_model=SummaryRead,
)
async def create_summary(note_id: int, db: DbSession) -> SummaryRead:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    summary = await summarize(note.content)
    return SummaryRead(note_id=note_id, summary=summary)


@router.post(
    "/notes/{note_id}/quiz",
    response_model=QuizRead,
)
async def create_quiz(note_id: int, db: DbSession) -> QuizRead:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    quiz = await generate_quiz(note.content)
    return QuizRead(note_id=note_id, questions=quiz.questions)


@router.post("/ask", response_model=AskRead)
async def ask(payload: AskRequest, db: DbSession) -> AskRead:
    return await answer_from_notes(db, payload.question)
