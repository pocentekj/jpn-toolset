import sqlite3

from .config import DB_PATH
from .dict_entry import DictEntry


def _row_to_entry(row: sqlite3.Row) -> DictEntry:
    return DictEntry(
        headword=row["headword"],
        reading=row["reading"],
        gloss=row["gloss"],
    )


def make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -20000")

    return conn


def search_entries(term: str) -> list[DictEntry]:
    conn = make_connection()
    conn.row_factory = sqlite3.Row

    with conn:
        cur = conn.execute(
            """
            SELECT headword, reading, gloss
            FROM words
            WHERE headword = ?
               OR reading = ?
               OR headword LIKE ?
            ORDER BY
                CASE
                    WHEN headword = ? THEN 0
                    WHEN reading = ? THEN 1
                    ELSE 2
                END,
                LENGTH(headword),
                headword
            LIMIT 50
            """,
            (term, term, f"{term}%", term, term),
        )
        return [_row_to_entry(row) for row in cur.fetchall()]
