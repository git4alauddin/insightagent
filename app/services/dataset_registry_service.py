import sqlite3
from datetime import datetime, timezone

from app.db.database import db_cursor
from app.db.schema import create_tables


class DatasetRegistryError(Exception):
    pass


def _raise_db_error(exc: sqlite3.Error) -> None:
    raise DatasetRegistryError("Database operation failed.") from exc


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_dataset_metadata(
    dataset_id: str,
    filename: str,
    storage_path: str,
    row_count: int,
    column_count: int,
    session_id: str | None = None,
) -> None:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO datasets (
                    dataset_id,
                    session_id,
                    filename,
                    storage_path,
                    row_count,
                    column_count,
                    uploaded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    session_id,
                    filename,
                    storage_path,
                    row_count,
                    column_count,
                    _utc_now_iso(),
                ),
            )
    except sqlite3.Error as exc:
        _raise_db_error(exc)


def get_dataset_metadata(dataset_id: str) -> dict[str, object]:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT dataset_id, session_id, filename, storage_path, row_count, column_count, uploaded_at
                FROM datasets
                WHERE dataset_id = ?
                """,
                (dataset_id,),
            )
            row = cursor.fetchone()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    if row is None:
        raise DatasetRegistryError(f"Dataset not found: {dataset_id}")

    return {
        "dataset_id": row["dataset_id"],
        "session_id": row["session_id"],
        "filename": row["filename"],
        "storage_path": row["storage_path"],
        "row_count": row["row_count"],
        "column_count": row["column_count"],
        "uploaded_at": row["uploaded_at"],
    }
