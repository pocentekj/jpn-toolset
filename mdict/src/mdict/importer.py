import time
import sqlite3
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from .config import DICT_PATH
from .db import make_connection


@dataclass
class DictEntry:
    headword: str
    reading: str | None
    gloss: str


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"


def _parse_entry(entry: ET.Element) -> DictEntry | None:
    headwords = [k.text for k in entry.findall("k_ele/keb") if k.text]

    if not headwords:
        return None

    readings = [r.text for r in entry.findall("r_ele/reb") if r.text]

    glosses = [
        g.text
        for g in entry.findall("sense/gloss")
        if g.text
        and g.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "eng") == "eng"
    ]
    glosses = list(dict.fromkeys(glosses))

    if not glosses:
        return None

    # first headword + first reading
    headword = headwords[0]
    reading = readings[0] if readings else None

    return DictEntry(
        headword=headword,
        reading=reading,
        gloss="; ".join(glosses),
    )


def _save_entries(conn: sqlite3.Connection, entries: list[DictEntry]) -> None:
    conn.executemany(
        """
        INSERT INTO words (headword, reading, gloss)
        VALUES (?, ?, ?)
        """,
        ((e.headword, e.reading, e.gloss) for e in entries),
    )


def run() -> int:
    tree = ET.parse(DICT_PATH)
    root = tree.getroot()

    count = 0
    entries: list[DictEntry] = []

    with make_connection() as conn:
        for entry in root.findall("entry"):
            dict_entry = _parse_entry(entry)
            if dict_entry is None:
                continue
            entries.append(dict_entry)
            count += 1
            if count % 500 == 0:
                _save_entries(conn, entries)
                entries = []

        if entries:
            _save_entries(conn, entries)

    print(f"Imported {count} words")
    return 0


def main() -> int:
    start_time = time.perf_counter()
    result = run()
    end_time = _format_timestamp(time.perf_counter() - start_time)
    print(f"Done in {end_time}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
