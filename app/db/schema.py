from app.db.database import db_cursor


def _ensure_sessions_columns(cursor) -> None:
    cursor.execute("PRAGMA table_info(sessions)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "title" not in existing_columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN title TEXT")

    if "status" not in existing_columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")


def _ensure_datasets_columns(cursor) -> None:
    cursor.execute("PRAGMA table_info(datasets)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "session_id" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN session_id TEXT")

    if "filename" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN filename TEXT NOT NULL DEFAULT ''")

    if "storage_path" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN storage_path TEXT NOT NULL DEFAULT ''")

    if "row_count" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN row_count INTEGER NOT NULL DEFAULT 0")

    if "column_count" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN column_count INTEGER NOT NULL DEFAULT 0")

    if "uploaded_at" not in existing_columns:
        cursor.execute("ALTER TABLE datasets ADD COLUMN uploaded_at TEXT NOT NULL DEFAULT ''")


def create_tables() -> None:
    with db_cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                title TEXT,
                status TEXT NOT NULL DEFAULT 'active'
            )
            """
        )

        _ensure_sessions_columns(cursor)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                token_estimate INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                session_id TEXT,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )

        _ensure_datasets_columns(cursor)
