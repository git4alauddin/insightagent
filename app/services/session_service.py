import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.db.database import db_cursor
from app.db.schema import create_tables


class SessionServiceError(Exception):
    pass


def _raise_db_error(exc: sqlite3.Error) -> None:
    raise SessionServiceError("Database operation failed.") from exc


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_session(session_id: str | None = None, title: str | None = None) -> str:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    resolved_session_id = session_id or str(uuid4())
    now = _utc_now_iso()

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions (session_id, created_at, updated_at, title, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (resolved_session_id, now, now, title, "active"),
            )
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    return resolved_session_id


def session_exists(session_id: str) -> bool:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    try:
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    return row is not None


def append_message(
    session_id: str,
    role: str,
    content: str,
    token_estimate: int = 0,
) -> None:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    if not session_exists(session_id):
        raise SessionServiceError(f"Session not found: {session_id}")

    now = _utc_now_iso()

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (session_id, role, content, created_at, token_estimate)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, now, token_estimate),
            )
            cursor.execute(
                """
                UPDATE sessions
                SET updated_at = ?
                WHERE session_id = ?
                """,
                (now, session_id),
            )
    except sqlite3.Error as exc:
        _raise_db_error(exc)


def get_recent_messages(session_id: str, limit: int = 20) -> list[dict[str, object]]:
    try:
        create_tables()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    if not session_exists(session_id):
        raise SessionServiceError(f"Session not found: {session_id}")

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT role, content, created_at, token_estimate
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
    except sqlite3.Error as exc:
        _raise_db_error(exc)

    chronological_rows = list(reversed(rows))
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"],
            "token_estimate": row["token_estimate"],
        }
        for row in chronological_rows
    ]


def format_context_for_llm(session_id: str, limit: int = 20) -> list[dict[str, str]]:
    messages = get_recent_messages(session_id, limit=limit)
    return [{"role": str(msg["role"]), "content": str(msg["content"])} for msg in messages]
