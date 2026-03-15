from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from rag.models import RagDocument


def get_loader(document: RagDocument):

    if document.file_type == ".docx":
        return Docx2txtLoader(document.file_path)

    if document.file_type == ".pdf":
        return PyMuPDFLoader(document.file_path)

    raise ValueError(f"지원하지 않는 파일 타입: {document.file_type}")