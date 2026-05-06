import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "insightagent.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_cursor():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    finally:
        connection.close()
