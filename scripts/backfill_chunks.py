import asyncio

from sqlalchemy import exists, select

from app.database import SessionLocal
from app.models import Note, NoteChunk
from app.services.rag import index_note

"""Chunk and embed every note that has no chunks yet.

Run from the project root: python -m scripts.backfill_chunks
"""

async def main() -> None:
    async with SessionLocal() as db:
        query = select(Note).where(~exists().where(NoteChunk.note_id == Note.id))

        notes = list(await db.scalars(query))

        print(f"{len(notes)} notes need indexing")
        for note in notes:
            await index_note(db, note)
            await db.commit()
            print(f"Indexed note {note.id}")


if __name__ == "__main__":
    asyncio.run(main())
