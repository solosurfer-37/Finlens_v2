import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings

CHUNK_SIZE = 1024 * 1024  # 1 MB
ALLOWED_EXTENSIONS = {".csv"}


def save_upload(file: UploadFile) -> Path:
    """Validate and safely store an uploaded CSV. Returns the path on disk.

    The user-supplied filename is never used in the disk path.
    """
    original_name = Path(file.filename or "").name
    if Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are allowed",
        )

    upload_dir = Path(settings.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4().hex}.csv"

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    written = 0
    with file_path.open("wb") as buffer:
        while chunk := file.file.read(CHUNK_SIZE):
            written += len(chunk)
            if written > max_bytes:
                buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File exceeds {settings.max_upload_size_mb} MB limit",
                )
            buffer.write(chunk)

    return file_path