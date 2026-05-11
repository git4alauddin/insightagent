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


def _ensure_documents_columns(cursor) -> None:
    cursor.execute("PRAGMA table_info(documents)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "session_id" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN session_id TEXT")

    if "filename" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN filename TEXT NOT NULL DEFAULT ''")

    if "storage_path" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN storage_path TEXT NOT NULL DEFAULT ''")

    if "file_extension" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN file_extension TEXT NOT NULL DEFAULT ''")

    if "file_size_bytes" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN file_size_bytes INTEGER NOT NULL DEFAULT 0")

    if "status" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN status TEXT NOT NULL DEFAULT 'uploaded'")

    if "uploaded_at" not in existing_columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN uploaded_at TEXT NOT NULL DEFAULT ''")


def _ensure_document_chunks_columns(cursor) -> None:
    cursor.execute("PRAGMA table_info(document_chunks)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "document_id" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN document_id TEXT NOT NULL DEFAULT ''"
        )

    if "filename" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN filename TEXT NOT NULL DEFAULT ''"
        )

    if "chunk_index" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN chunk_index INTEGER NOT NULL DEFAULT 0"
        )

    if "text" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN text TEXT NOT NULL DEFAULT ''"
        )

    if "page" not in existing_columns:
        cursor.execute("ALTER TABLE document_chunks ADD COLUMN page INTEGER")

    if "embedding_json" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN embedding_json TEXT NOT NULL DEFAULT '[]'"
        )

    if "created_at" not in existing_columns:
        cursor.execute(
            "ALTER TABLE document_chunks ADD COLUMN created_at TEXT NOT NULL DEFAULT ''"
        )


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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                session_id TEXT,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                status TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )

        _ensure_documents_columns(cursor)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                page INTEGER,
                embedding_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(document_id)
            )
            """
        )

        _ensure_document_chunks_columns(cursor)
