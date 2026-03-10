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
                on_readings_norm,
                kun_readings,
                meaning,
                components,
                freq
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(kanji) DO UPDATE SET
                on_readings = excluded.on_readings,
                on_readings_norm = excluded.on_readings_norm,
                kun_readings = excluded.kun_readings,
                meaning = excluded.meaning,
                components = excluded.components,
                freq = excluded.freq
            """,
            (
                entry.kanji,
                entry.on_readings,
                entry.on_readings_norm,
                entry.kun_readings,
                entry.meaning,
                entry.components,
                entry.freq,
            ),
        )
