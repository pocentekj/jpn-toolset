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

    def _row_to_entry(self, row: sqlite3.Row) -> KanjiEntry:
        return cast(
            KanjiEntry,
            {
                "kanji": row["kanji"],
                "readings": {
                    "on": row["on_readings"] or "",
                    "kun": row["kun_readings"] or "",
                },
                "meaning": row["meaning"],
                "components": {
                    "ids": row["ids"],
                    "radicals": [],
                },
            },
        )

    def by_kanji(self, kanji: str) -> list[KanjiEntry]:
        cur = self._conn.execute(
            """
            SELECT kanji, on_readings, kun_readings, meaning, ids
            FROM kanjis
            WHERE kanji = ?
            """,
            (kanji,),
        )

        return [self._row_to_entry(row) for row in cur.fetchall()]

    def by_readings(self, reading: str) -> list[KanjiEntry]:
        cur = self._conn.execute(
            """
            SELECT kanji, on_readings, kun_readings, meaning, ids
            FROM kanjis
            WHERE on_readings LIKE ?
               OR kun_readings LIKE ?
            """,
            (f"%{reading}%", f"%{reading}%"),
        )

        return [self._row_to_entry(row) for row in cur.fetchall()]
