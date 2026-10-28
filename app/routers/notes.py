from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.auth import require_api_key
from app.database import DbSession
from app.models import Note
from app.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(require_api_key)],
)


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, db: DbSession) -> Note:
    new_note = Note(**payload.model_dump())

    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


@router.get("", response_model=list[NoteRead], status_code=status.HTTP_200_OK)
async def get_notes(db: DbSession) -> list[Note]:
    result = await db.scalars(select(Note))
    return list(result)


@router.get("/{note_id}", response_model=NoteRead, status_code=status.HTTP_200_OK)
async def get_note(note_id: int, db: DbSession) -> Note:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note


@router.patch("/{note_id}", response_model=NoteRead, status_code=status.HTTP_200_OK)
async def patch_note(note_id: int, payload: NoteUpdate, db: DbSession) -> Note:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    changes = payload.model_dump(exclude_unset=True)
    if None in changes.values():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="You cannot leave a field null!",
        )

    for key, value in changes.items():
        setattr(note, key, value)

    await db.commit()

    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: DbSession) -> None:
    note = await db.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    await db.delete(note)
    await db.commit()
