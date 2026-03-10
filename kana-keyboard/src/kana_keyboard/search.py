import os
import sqlite3
from pathlib import Path
from typing import cast

from .types import KanjiEntry

KANJIS_DB = Path(os.environ.get("HOME", ".")) / ".local" / "share" / "kanjis.sqlite"


def make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(KANJIS_DB)

    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -20000")

    return conn

class SearchProvider:
    """Proxy class for search. Currently backed by SQLite."""

    def __init__(self) -> None:
        self._conn = make_connection()
        self._conn.row_factory = sqlite3.Row

    def __enter__(self) -> "SearchProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._conn.close()

    def _row_to_entry(self, row: sqlite3.Row) -> KanjiEntry:
        return cast(
            KanjiEntry,
            {
                "kanji": row["kanji"],
                "on_readings": row["on_readings"],
                "kun_readings": row["kun_readings"],
                "meaning": row["meaning"],
            },
        )

    def by_kanji(self, kanji: str) -> list[KanjiEntry]:
        cur = self._conn.execute(
            """
            SELECT kanji, on_readings, kun_readings, meaning
            FROM kanjis
            WHERE kanji = ?
            """,
            (kanji,),
        )

        return [self._row_to_entry(row) for row in cur.fetchall()]

    def by_readings(self, reading: str) -> list[KanjiEntry]:
        cur = self._conn.execute(
            """
            SELECT kanji, on_readings, kun_readings, meaning
            FROM kanjis
            WHERE on_readings LIKE ?
               OR on_readings_norm LIKE ?
               OR kun_readings LIKE ?
            ORDER BY freq
            """,
            (f"%{reading}%", f"%{reading}%", f"%{reading}%"),
        )

        return [self._row_to_entry(row) for row in cur.fetchall()]
