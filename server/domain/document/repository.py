# repository/document_repository.py

from sqlalchemy.orm import Session
from domain.document.models import Document
from datetime import date
from pydantic import BaseModel
from core.file_utils import FileInfo


class DocumentRepository:

    def get_documents(self, db: Session):
        # 조회: commit 필요 없음
        return db.query(Document).order_by(Document.uploaded_at.desc()).all()

    def save_document(
        self,
        db: Session,
        file_info: FileInfo,
        expire_at: date,
    ) -> Document:

        doc = Document(
            file_name=file_info.file_name,
            file_path=file_info.file_path,
            file_size=file_info.file_size,
            uploaded_by="system",
            expire_at=expire_at,
        )

        db.add(doc)
        return doc
