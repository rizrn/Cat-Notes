import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response


async def add_process_time(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()  # Monotonic clock instead of wall clock
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response


async def add_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    field = "X-Request-ID"
    request_id = request.headers.get(field)

    # Initialise new request_id if required or old id too big
    if request_id is None or len(request_id) > 128:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    response = await call_next(request)

    response.headers[field] = request_id
    return response
