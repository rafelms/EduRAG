"""Rotas de perguntas (RF05 a RF07)."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from httpx import HTTPError

from app.api.routes_documents import ServicesDep
from app.api.schemas import AskRequest, AskResponse, LLMInfo, QuestionOut, QuestionsPage
from app.ports.llm import LLMUnavailableError

router = APIRouter(tags=["perguntas"])


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, services: ServicesDep) -> AskResponse:
    try:
        answer = services.qa.ask(body.question, body.document_ids, body.top_k)
    except (HTTPError, LLMUnavailableError) as exc:
        # HTTPError vem do Ollama (embeddings ou LLM local); LLMUnavailableError, do Claude.
        raise HTTPException(502, "O serviço de modelos não respondeu.") from exc
    return AskResponse(
        question_id=answer.question_id,
        answer=answer.answer,
        sources=[asdict(s) for s in answer.sources],
    )


@router.get("/llm", response_model=LLMInfo)
def llm_info(services: ServicesDep) -> LLMInfo:
    settings = services.settings
    return LLMInfo(
        provider=settings.llm_provider,
        model=services.llm.model_name,
        effort=settings.llm_effort if settings.llm_provider == "claude" else None,
    )


@router.get("/questions", response_model=QuestionsPage)
def list_questions(
    services: ServicesDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> QuestionsPage:
    records, total = services.repository.list_questions(limit, offset)
    return QuestionsPage(
        items=[QuestionOut(**vars(r)) for r in records],
        total=total,
        limit=limit,
        offset=offset,
    )
