import os
import uuid
import shutil
from fastapi import UploadFile
from pydantic import BaseModel


class FileInfo(BaseModel):
    file_name: str
    file_path: str
    file_size: int
    file_type: str


async def save_upload_file(file: UploadFile, directory: str):
    os.makedirs(directory, exist_ok=True)

    original_name = file.filename or "unnamed_file"
    ext = os.path.splitext(original_name)[1]

    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(directory, safe_name)

    # stream 방식 저장 (메모리 안전)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    return FileInfo(
        file_name=original_name,
        file_path=file_path,
        file_size=file_size,
        file_type=ext,
    )
