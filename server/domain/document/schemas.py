from pydantic import BaseModel, ConfigDict
from datetime import date


class DocumentDTO(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_size: int
    uploaded_by: str
    uploaded_at: str
    expire_at: str
    status: str = "active"

    @classmethod
    def from_entity(cls, doc):
        return cls(
            id=doc.id,
            file_name=doc.file_name,
            file_path=doc.file_path,
            file_size=doc.file_size,
            uploaded_by=doc.uploaded_by,
            uploaded_at=doc.uploaded_at.isoformat() if doc.uploaded_at else "",
            expire_at=doc.expire_at.isoformat() if doc.expire_at else "",
            status=getattr(doc, "status", "active"),
        )


class DocumentCreate(BaseModel):
    file_name: str
    file_path: str
    file_size: int
    uploaded_by: str
    expire_at: date
