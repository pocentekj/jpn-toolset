import os
import sqlite3
from pathlib import Path
from collections.abc import Iterable

from .kanji import Kanji

KANJIS_DB = Path(os.environ.get("HOME", ".")) / ".local" / "share" / "kanjis.sqlite"


def make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(KANJIS_DB)

    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -20000")

    return conn


def save_kanjis(entries: Iterable[Kanji]) -> None:
    rows = []

    for entry in entries:
        rows.append(
            (
                entry.kanji,
                entry.on_readings,
                entry.on_readings_norm,
                entry.kun_readings,
                entry.name_readings,
                entry.meaning,
                entry.components,
                entry.freq,
            )
        )

    with make_connection() as conn:
        conn.executemany(
            """
            INSERT INTO kanjis (
                kanji,
                on_readings,
                on_readings_norm,
                kun_readings,
                name_readings,
                meaning,
                components,
                freq
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(kanji) DO UPDATE SET
                on_readings = excluded.on_readings,
                on_readings_norm = excluded.on_readings_norm,
                kun_readings = excluded.kun_readings,
                name_readings = excluded.name_readings,
                meaning = excluded.meaning,
                components = excluded.components,
                freq = excluded.freq
            """,
            rows,
        )
