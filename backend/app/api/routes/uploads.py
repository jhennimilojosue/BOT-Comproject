from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.schemas.api_schemas import UploadResponse

router = APIRouter(prefix="/api/v1", tags=["uploads"])

MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".xlsx"}


def get_upload_repository():
    raise NotImplementedError("Dependency injection pending Dev 1 interfaces")


@router.post("/uploads", response_model=UploadResponse, status_code=201)
async def upload_file(file: UploadFile, upload_repository=Depends(get_upload_repository)):
    if not file.filename or not file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": "Only .xlsx files are allowed"}},
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": "El archivo excede el tamaño máximo permitido (50 MB)"}},
        )

    upload = {
        "id": str(uuid4()),
        "file_name": file.filename,
        "status": "UPLOADED",
        "created_at": datetime.utcnow(),
    }

    try:
        saved = upload_repository.save(upload)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Error registering upload"}},
        )

    return UploadResponse(**saved)
