from fastapi import Depends

from domain.document.repository import DocumentRepository
from domain.document.service import DocumentService


def get_document_repository() -> DocumentRepository:
    return DocumentRepository()


def get_document_service(
    repo: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    return DocumentService(repo)
