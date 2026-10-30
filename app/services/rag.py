import re

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, NoteChunk
from app.schemas import AskRead, AskSource
from app.services.llm import answer_question, embed_documents, embed_query

NO_ANSWER = "I couldn't find the answer in your notes."


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    current: list[str] = []
    current_len = 0
    chunks: list[str] = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        added_len = len(sentence) if not current else current_len + 1 + len(sentence)

        if current and added_len > max_chars:
            chunks.append(" ".join(current))
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len = added_len

    if current:
        chunks.append(" ".join(current))

    return chunks


async def index_note(db: AsyncSession, note: Note) -> None:
    await db.execute(delete(NoteChunk).where(NoteChunk.note_id == note.id))
    chunks = chunk_text(note.content)
    vectors = await embed_documents(chunks)

    for chunk_i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        db.add(
            NoteChunk(
                note_id=note.id,
                chunk_index=chunk_i,
                content=chunk,
                embedding=vector,
            )
        )


async def search_chunks(
    db: AsyncSession, question: str, limit: int = 4, max_distance: float = 0.45
) -> list[tuple[NoteChunk, str, float]]:
    vector = await embed_query(question)
    distance = NoteChunk.embedding.cosine_distance(vector)

    query = (
        select(NoteChunk, Note.title, distance.label("distance"))
        .join(Note)
        .where(distance < max_distance)
        .order_by(distance)
        .limit(limit)
    )
    res = await db.execute(query)
    return [(chunk, title, float(dist)) for chunk, title, dist in res]


async def answer_from_notes(db: AsyncSession, question: str) -> AskRead:
    results = await search_chunks(db, question)

    if not results:
        return AskRead(answer=NO_ANSWER, sources=[])

    contexts = [chunk.content for chunk, _title, _distance in results]
    answer = await answer_question(question, contexts)

    sources = [
        AskSource(note_id=chunk.note_id, title=title, excerpt=chunk.content)
        for chunk, title, _distance in results
    ]

    return AskRead(answer=answer, sources=sources)
