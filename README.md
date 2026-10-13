# Cat Notes :smiley_cat:

A simplified AI-powered note-taking API with customizable cat references.

## Features

- [X] API-based Note taking
- [X] PostgreSQL integration to keep track of your notes
- [ ] AI-powered summaries
- [ ] Cats! :heart_eyes_cat:

## Quick start

Prerequisites:
- Python 3.12
- Docker Desktop

To run this project (commands for PowerShell or bash):
```bash
# 1. Create your local config
cp .env.example .env              # Windows cmd: copy .env.example .env
# Then edit .env: set POSTGRES_PASSWORD, and use the user "postgres"
# with that same password in DATABASE_URL

# 2. Start Postgres
docker compose up -d

# 3. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\Activate.ps1        # cmd: .venv\Scripts\activate.bat
                                  # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 4. Create the database tables and start the API
alembic upgrade head
uvicorn app.main:app --reload
```

## About this project

This is a Python project that uses the following tech stack:
- Docker
- PostgreSQL
- FastAPI
- Pydantic
- SQLAlchemy with asyncpg, Alembic
- (Planned) Ollama

## API Endpoints

Interactive docs are available at `http://localhost:8000/docs` while the server is running.

| Method | Path | Description | Success |
|---|---|---|---|
| `POST` | `/notes` | Create a note | `201 Created` |
| `GET` | `/notes` | List all notes | `200 OK` |
| `GET` | `/notes/{note_id}` | Get one note | `200 OK` |
| `PATCH` | `/notes/{note_id}` | Update some fields of a note | `200 OK` |
| `DELETE` | `/notes/{note_id}` | Delete a note | `204 No Content` |

### Note fields

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Set by the database |
| `title` | string | Required, 1–200 characters |
| `content` | string | Required, 1–5000 characters |
| `author` | string | Required, 1–200 characters |
| `created_at` | datetime (UTC) | Set by the database |

`PATCH` only changes the fields you send. Leaving a field out keeps its current value; sending it as `null` is rejected.

### Errors

| Status | When |
|---|---|
| `404 Not Found` | No note exists with that `note_id` |
| `422 Unprocessable Content` | Invalid body (missing field, wrong length, `null` in a `PATCH`) or a non-integer `note_id` |

### Example

```bash
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Photosynthesis", "content": "Plants convert light into chemical energy.", "author": "John"}'
```

```json
{
  "id": 1,
  "title": "Photosynthesis",
  "content": "Plants convert light into chemical energy.",
  "author": "John",
  "created_at": "2026-10-13T09:30:00Z"
}
```

## Project structure

```
notes-assistant/
├── app/
│   ├── main.py            # FastAPI app and router includes
│   ├── config.py          # Settings loaded from .env (pydantic-settings)
│   ├── database.py        # Async engine, session factory, get_db dependency
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response models
│   └── routers/
│       └── notes.py       # CRUD endpoints for notes
├── alembic/               # Migration scripts
├── docker-compose.yml     # Postgres (pgvector) service
├── requirements.txt
├── .env
└── .env.example
```

## Roadmap

- [X] **REST + PostgreSQL** — CRUD for notes, Pydantic schemas, Alembic migrations
- [ ] **Middleware** — request ID, timing (`X-Process-Time`), logging, CORS,
  consistent error responses, API-key auth
- [ ] **AI endpoints** — `POST /notes/{id}/summary`, `POST /notes/{id}/quiz`
  (JSON output validated with Pydantic)
- [ ] **RAG** — enable pgvector, chunk + embed notes on save, `POST /ask`
- [ ] **Polish** — pytest coverage, Docker Compose for the full app