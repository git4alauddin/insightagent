import sqlite3
from datetime import datetime, timezone

from app.db.database import db_cursor
from app.db.schema import create_tables


class DocumentRegistryError(Exception):
    pass


def _raise_db_error(exc: sqlite3.Error) -> None:
    raise DocumentRegistryError("Database operation failed.") from exc


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_document_metadata(
    document_id: str,
    filename: str,
    storage_path: str,
    file_extension: str,
    file_size_bytes: int,
    session_id: str | None = None,
    status: str = "uploaded",
) -> None:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    document_id,
                    session_id,
                    filename,
                    storage_path,
                    file_extension,
                    file_size_bytes,
                    status,
                    uploaded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    session_id,
                    filename,
                    storage_path,
                    file_extension,
                    file_size_bytes,
                    status,
                    _utc_now_iso(),
                ),
            )
    except sqlite3.Error as exc:
        _raise_db_error(exc)


def get_document_metadata(document_id: str) -> dict[str, object]:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    document_id,
                    session_id,
                    filename,
                    storage_path,
                    file_extension,
                    file_size_bytes,
                    status,
                    uploaded_at
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            )
            row = cursor.fetchone()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    if row is None:
        raise DocumentRegistryError(f"Document not found: {document_id}")

    return {
        "document_id": row["document_id"],
        "session_id": row["session_id"],
        "filename": row["filename"],
        "storage_path": row["storage_path"],
        "file_extension": row["file_extension"],
        "file_size_bytes": row["file_size_bytes"],
        "status": row["status"],
        "uploaded_at": row["uploaded_at"],
    }
