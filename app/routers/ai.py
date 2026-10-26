from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.models import Note
from app.schemas import SummaryRead
from app.services.llm import summarize

router = APIRouter(
    prefix="/notes", tags=["ai"], dependencies=[Depends(require_api_key)]
)

db_session = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/{note_id}/summary",
    response_model=SummaryRead,
)
async def get_summary(note_id: int, db: db_session) -> SummaryRead:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    summary = await summarize(note.content)
    return SummaryRead(
        note_id=note_id,
        summary=summary
    )
