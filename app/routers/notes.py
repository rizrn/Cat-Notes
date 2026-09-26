from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])

notes: dict[int, NoteRead] = {}
next_id = 1


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate) -> NoteRead:
    global next_id
    # We must grab timezone.utc to avoid user updating notes and cause a backward time shift
    new_note = NoteRead(
        id=next_id, **payload.model_dump(), created_at=datetime.now(timezone.utc)
    )
    notes[next_id] = new_note
    next_id += 1
    return new_note


@router.get("", response_model=list[NoteRead], status_code=status.HTTP_200_OK)
async def get_notes() -> list[NoteRead]:
    return list(notes.values())


@router.get("/{note_id}", response_model=NoteRead, status_code=status.HTTP_200_OK)
async def get_note(note_id: int) -> NoteRead:
    if note_id not in notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return notes[note_id]


@router.patch("/{note_id}", response_model=NoteRead, status_code=status.HTTP_200_OK)
async def patch_note(note_id: int, payload: NoteUpdate) -> NoteRead:
    if note_id not in notes:
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

    existing_note = notes[note_id]
    updated = existing_note.model_copy(update=changes)
    notes[note_id] = updated

    return updated


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int) -> None:
    if note_id not in notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    del notes[note_id]
