import time
import sqlite3
import xml.etree.ElementTree as ET

from .config import DICT_PATH
from .dict_entry import DictEntry
from .db import make_connection


def _format_timestamp(seconds: float) -> str:
    if seconds >= 24 * 3600:
        return f"{seconds:.2f}s"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    parts: list[str] = []

    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs:.2f}s")

    return " ".join(parts)


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
                print(".", end="")
                entries = []

        if entries:
            _save_entries(conn, entries)

        print("")

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
