#!/usr/bin/env python
#
# Display 1000 most frequently used kanjis (according to KANJIDIC2)
import xml.etree.ElementTree as ET
from pathlib import Path

KANJIDIC_FILE = Path(__file__).parent.parent.parent / "kanshudo-scraper" / "data" / "kanjidic2.xml"


def top_kanji_by_freq(path: str, limit: int = 1000) -> list[str]:
    root = ET.parse(path).getroot()
    items: list[tuple[int, str]] = []

    for ch in root.findall("character"):
        literal = ch.findtext("literal")
        freq_text = ch.findtext("misc/freq")
        if not literal or not freq_text:
            continue
        items.append((int(freq_text), literal))

    items.sort(key=lambda x: x[0])
    return [kanji for _, kanji in items[:limit]]


if __name__ == "__main__":
    for kanji in top_kanji_by_freq(KANJIDIC_FILE, 1000):
        print(kanji, end="")
