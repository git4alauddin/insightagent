from datetime import datetime, timezone
from uuid import uuid4

from app.db.database import db_cursor
from app.db.schema import create_tables


class SessionServiceError(Exception):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_session(session_id: str | None = None) -> str:
    create_tables()

    resolved_session_id = session_id or str(uuid4())
    now = _utc_now_iso()

    with db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sessions (session_id, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (resolved_session_id, now, now),
        )

    return resolved_session_id


def session_exists(session_id: str) -> bool:
    create_tables()

    with db_cursor() as cursor:
        cursor.execute(
            "SELECT session_id FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()

    return row is not None


def append_message(
    session_id: str,
    role: str,
    content: str,
    token_estimate: int = 0,
) -> None:
    create_tables()

    if not session_exists(session_id):
        raise SessionServiceError(f"Session not found: {session_id}")

    now = _utc_now_iso()

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


def get_recent_messages(session_id: str, limit: int = 20) -> list[dict[str, object]]:
    create_tables()

    if not session_exists(session_id):
        raise SessionServiceError(f"Session not found: {session_id}")

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
