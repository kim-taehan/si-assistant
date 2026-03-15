import os
from dataclasses import dataclass


@dataclass
class RagDocument:
    id: str
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    status: str

    @classmethod
    def from_entity(cls, doc):
        return cls(
            id=str(doc.id),
            file_name=doc.file_name,
            file_path=doc.file_path,
            file_size=doc.file_size,
            file_type=os.path.splitext(doc.file_name)[1],
            status=getattr(doc, "status", "active"),
        )
