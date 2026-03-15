from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from domain.document.repository import DocumentRepository
from domain.document.schemas import DocumentDTO
from core.file_utils import save_upload_file
from rag.ingest_service import add_document
from rag.models import RagDocument

# from rag.document import Document
# from rag.service import add_document


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    def get_documents(self, db: Session):
        docs = self.repo.get_documents(db)

        # from_orm 사용
        return [DocumentDTO.from_entity(doc) for doc in docs]

    def _parse_expire_date(self, expire_at: str):
        try:
            return datetime.strptime(expire_at, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD",
            )

    async def upload_file(self, db: Session, file: UploadFile, expire_at: str):

        file_info = await save_upload_file(file, "./.cache/files")
        doc = self.repo.save_document(db, file_info, self._parse_expire_date(expire_at))

        add_document(RagDocument.from_entity(doc))

        db.commit()
        db.refresh(doc)
        return DocumentDTO.from_entity(doc)
