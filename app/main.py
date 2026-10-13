"""Cria o app FastAPI e registra as rotas."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from app.api import routes_ask, routes_documents, routes_health
from app.config import get_settings
from app.container import Services, build_services
from app.logging_config import configure_logging, request_id_var

logger = logging.getLogger("edurag.access")


def create_app(services: Services | None = None) -> FastAPI:
    settings = services.settings if services else get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="EduRAG", version="0.1.0")
    app.state.services = services or build_services(settings)

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            request_id_var.reset(token)
        response.headers["x-request-id"] = request_id
        # Só método, rota e status: nunca o conteúdo da requisição.
        logger.info(
            "requisição",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    app.include_router(routes_health.router)
    app.include_router(routes_documents.router)
    app.include_router(routes_ask.router)
    return app


app = create_app()
