"""Saúde da aplicação (RF08)."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.routes_documents import ServicesDep

logger = logging.getLogger(__name__)

router = APIRouter(tags=["saúde"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: o processo está de pé."""
    return {"status": "ok"}


@router.get("/ready")
def ready(services: ServicesDep) -> JSONResponse:
    """Readiness: banco, embeddings (Ollama) e LLM (Ollama ou Claude) respondem."""
    checks = {
        "database": services.repository.ping,
        "embeddings": services.embeddings.ping,
        "llm": services.llm.ping,
    }
    failed: list[str] = []
    for name, check in checks.items():
        try:
            check()
        except Exception:
            logger.warning("componente indisponível", extra={"component": name})
            failed.append(name)

    if failed:
        return JSONResponse(status_code=503, content={"status": "unavailable", "failed": failed})
    return JSONResponse(content={"status": "ready"})
