import json
import sqlite3
from datetime import datetime, timezone

from app.db.database import db_cursor
from app.db.schema import create_tables
from app.schemas.document import DocumentChunk


class DocumentVectorStoreError(Exception):
    pass


def save_document_chunks(
    document_id: str,
    chunks: list[DocumentChunk],
    embeddings_by_chunk_id: dict[str, list[float]],
) -> None:
    if not chunks:
        raise DocumentVectorStoreError("At least one document chunk is required.")

    _validate_chunk_embeddings(document_id, chunks, embeddings_by_chunk_id)

    try:
        create_tables()
    except sqlite3.Error as exc:
        raise DocumentVectorStoreError("Database operation failed.") from exc

    created_at = _utc_now_iso()

    try:
        with db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM document_chunks WHERE document_id = ?",
                (document_id,),
            )

            cursor.executemany(
                """
                INSERT INTO document_chunks (
                    chunk_id,
                    document_id,
                    filename,
                    chunk_index,
                    text,
                    page,
                    embedding_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.filename,
                        chunk.chunk_index,
                        chunk.text,
                        chunk.page,
                        json.dumps(embeddings_by_chunk_id[chunk.chunk_id]),
                        created_at,
                    )
                    for chunk in chunks
                ],
            )
    except sqlite3.Error as exc:
        raise DocumentVectorStoreError("Database operation failed.") from exc


def get_document_chunks(document_id: str) -> list[dict[str, object]]:
    try:
        create_tables()
    except sqlite3.Error as exc:
        raise DocumentVectorStoreError("Database operation failed.") from exc

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    filename,
                    chunk_index,
                    text,
                    page,
                    embedding_json,
                    created_at
                FROM document_chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document_id,),
            )
            rows = cursor.fetchall()
    except sqlite3.Error as exc:
        raise DocumentVectorStoreError("Database operation failed.") from exc

    return [
        {
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "filename": row["filename"],
            "chunk_index": row["chunk_index"],
            "text": row["text"],
            "page": row["page"],
            "embedding": json.loads(row["embedding_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def _validate_chunk_embeddings(
    document_id: str,
    chunks: list[DocumentChunk],
    embeddings_by_chunk_id: dict[str, list[float]],
) -> None:
    for chunk in chunks:
        if chunk.document_id != document_id:
            raise DocumentVectorStoreError(
                "All chunks must belong to the requested document."
            )

        embedding = embeddings_by_chunk_id.get(chunk.chunk_id)
        if not embedding:
            raise DocumentVectorStoreError(
                f"Missing embedding for chunk: {chunk.chunk_id}"
            )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
