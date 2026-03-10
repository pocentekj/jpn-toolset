import os
import sqlite3
from pathlib import Path

from .kanji import Kanji

KANJIS_DB = Path(os.environ.get("HOME", ".")) / ".local" / "share" / "kanjis.sqlite"


def make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(KANJIS_DB)

    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -20000")

    return conn


def save_kanji(entry: Kanji) -> None:
    if not entry.kanji:
        raise ValueError("Kanji entry has no kanji character")

    with make_connection() as conn:
        conn.execute(
            """
            INSERT INTO kanjis (
                kanji,
                on_readings,
                kun_readings,
                meaning,
                ids,
                components
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(kanji) DO UPDATE SET
                on_readings = excluded.on_readings,
                kun_readings = excluded.kun_readings,
                meaning = excluded.meaning,
                ids = excluded.ids,
                components = excluded.components
            """,
            (
                entry.kanji,
                entry.readings.on,
                entry.readings.kun,
                entry.meaning,
                entry.components.ids,
                entry._components_text,
            ),
        )
