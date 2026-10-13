"""Rotas de documentos (RF01 a RF04)."""

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Response,
    UploadFile,
)

from app.api.schemas import DocumentCreated, DocumentOut
from app.container import Services

router = APIRouter(prefix="/documents", tags=["documentos"])


def get_services(request: Request) -> Services:
    services: Services = request.app.state.services
    return services


ServicesDep = Annotated[Services, Depends(get_services)]


@router.post("", status_code=202, response_model=DocumentCreated)
def upload_document(
    file: UploadFile, background: BackgroundTasks, services: ServicesDep
) -> DocumentCreated:
    filename = file.filename or "documento.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Apenas arquivos PDF são aceitos.")

    limit = services.settings.max_upload_bytes
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(
            413, f"O arquivo excede o limite de {services.settings.max_upload_mb} MB."
        )
    if not data.startswith(b"%PDF-"):
        raise HTTPException(400, "O arquivo não é um PDF válido.")

    document = services.repository.create_document(filename)
    background.add_task(services.ingestion.ingest, document.id, data)
    return DocumentCreated(id=document.id, status=document.status)


@router.get("", response_model=list[DocumentOut])
def list_documents(services: ServicesDep) -> list[DocumentOut]:
    return [DocumentOut(**vars(d)) for d in services.repository.list_documents()]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: UUID, services: ServicesDep) -> DocumentOut:
    document = services.repository.get_document(document_id)
    if document is None:
        raise HTTPException(404, "Documento não encontrado.")
    return DocumentOut(**vars(document))


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: UUID, services: ServicesDep) -> Response:
    if not services.repository.delete_document(document_id):
        raise HTTPException(404, "Documento não encontrado.")
    return Response(status_code=204)
