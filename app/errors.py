from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.llm import LLMUnavailableError


def error_body(
    request: Request,
    code: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    result = {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
        }
    }

    if details is not None:
        result["error"]["details"] = details
    return result


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details: list[dict[str, str]] = []
    # To not drop WWW-Authenticate header from auth.py
    errors = exc.errors()
    for error in errors:
        loc = error["loc"]
        message = error["msg"]
        field = ".".join(str(part) for part in loc[1:])

        details.append({"field": field, "message": message})

    return JSONResponse(
        error_body(request, "validation_error", "Invalid request", details),
        status_code=422,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")
    return JSONResponse(
        error_body(request, code, str(exc.detail)),
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def llm_exception_handler(
    request: Request, exc: LLMUnavailableError
) -> JSONResponse:
    return JSONResponse(
        error_body(
            request,
            "llm_unavailable",
            "The AI service is unavailable. Please try again later.",
        ),
        status_code=503,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(LLMUnavailableError, llm_exception_handler) # pyright: ignore[reportArgumentType]
