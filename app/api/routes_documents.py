from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.dependencies import require_api_key
from app.api.rate_limit import enforce_rate_limit
from app.config import settings
from app.schemas.document import (
    DocumentAskRequest,
    DocumentAskResponse,
    DocumentUploadResponse,
)
from app.services.document_answer_service import DocumentAnswerError, answer_document_question
from app.services.document_registry_service import (
    DocumentRegistryError,
    get_document_metadata,
    register_document_metadata,
)
from app.services.document_service import (
    DocumentServiceError,
    build_document_upload_response,
    validate_document_file,
)


router = APIRouter(
    tags=["documents"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)


def _ensure_document_exists(document_id: str) -> None:
    try:
        get_document_metadata(document_id)
    except DocumentRegistryError as exc:
        if "Document not found" in str(exc):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": str(exc),
                    }
                },
            ) from exc

        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DOCUMENT_DB_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc


@router.post("/documents/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DOCUMENT_VALIDATION_ERROR",
                    "message": "File name is required.",
                }
            },
        )

    file_bytes = file.file.read()

    try:
        file_extension = validate_document_file(file.filename, len(file_bytes))
    except DocumentServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "DOCUMENT_VALIDATION_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    document_id = f"doc_{uuid4().hex}"
    base_upload_dir = Path(settings.upload_dir) / "documents"
    target_folder = base_upload_dir / (session_id or "standalone")
    target_folder.mkdir(parents=True, exist_ok=True)
    target_path = target_folder / f"{document_id}{file_extension}"

    try:
        target_path.write_bytes(file_bytes)
        register_document_metadata(
            document_id=document_id,
            session_id=session_id,
            filename=file.filename,
            storage_path=str(target_path),
            file_extension=file_extension,
            file_size_bytes=len(file_bytes),
        )
        return build_document_upload_response(document_id, file.filename)
    except DocumentRegistryError as exc:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DOCUMENT_DB_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
    except OSError as exc:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DOCUMENT_STORAGE_ERROR",
                    "message": f"Document could not be stored: {exc}",
                }
            },
        ) from exc


@router.post("/documents/{document_id}/ask", response_model=DocumentAskResponse)
def ask_document_question(
    document_id: str,
    request: DocumentAskRequest,
) -> DocumentAskResponse:
    _ensure_document_exists(document_id)

    try:
        return answer_document_question(document_id, request.question)
    except DocumentAnswerError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "DOCUMENT_ANSWER_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
