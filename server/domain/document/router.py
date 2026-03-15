"""
Document Management API with RAG Integration.
"""

from fastapi import APIRouter, Depends, UploadFile, Form, Query, HTTPException
from domain.document.service import DocumentService
from dependencies.document import get_document_service
from sqlalchemy.orm import Session
from core.db import get_db


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return service.get_documents(db)


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    expire_at: str = Form(...),
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return await service.upload_file(db, file, expire_at)
