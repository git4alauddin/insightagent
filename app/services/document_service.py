from pathlib import Path

from app.config import settings
from app.schemas.document import DocumentUploadResponse


class DocumentServiceError(Exception):
    pass


def validate_document_file(file_name: str, file_size_bytes: int) -> str:
    extension = Path(file_name).suffix.lower()
    if extension not in settings.allowed_document_extensions:
        raise DocumentServiceError("Only PDF, TXT, and Markdown documents are supported.")

    max_size_bytes = settings.document_max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise DocumentServiceError(
            f"Document exceeds file size limit ({settings.document_max_file_size_mb} MB)."
        )

    if file_size_bytes <= 0:
        raise DocumentServiceError("Document file is empty.")

    return extension


def build_document_upload_response(
    document_id: str,
    filename: str,
) -> DocumentUploadResponse:
    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        status="uploaded",
    )
