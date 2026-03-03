import re
from typing import Dict, List, cast

from bs4 import BeautifulSoup, Tag

from .helpers import norm
from .kanji import Kanji


def find_grow_value(soup: BeautifulSoup, label: str):
    """
    Zwraca prawą kolumnę (div.col-3-4) dla wiersza, którego lewa kolumna
    (div.col-1-4...) ma tekst == label.
    """
    for row in soup.select("div.g-row"):
        left = row.select_one("div.col-1-4")
        if not left:
            continue
        if norm(left.get_text(" ", strip=True)) == label:
            return row.select_one("div.col-3-4")
    return None


def extract_reading_text(reading_div: Tag) -> str:
    # make copy - we can be sure that it's a Tag instance
    reading_div = cast(Tag, BeautifulSoup(str(reading_div), "lxml").div)

    # Remove unnecessary help/overlay/script elements
    for junk in reading_div.select(
        "[id$='_help'], .helptext, script, style, .help, .cover, .warning"
    ):
        junk.decompose()

    text = norm(reading_div.get_text(" ", strip=True))
    return text


def parse_h1_means(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    h1 = soup.find("h1")
    if not h1:
        return None, None
    txt = norm(h1.get_text(" ", strip=True))  # np. "年 means 'year'"
    m = re.match(r"^(?P<kanji>\S+)\s+means\s+'(?P<meaning>[^']+)'", txt)
    if not m:
        return None, None
    return m.group("kanji"), m.group("meaning")


def parse_common_readings(soup: BeautifulSoup) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    box = find_grow_value(soup, "Common readings")
    if not box:
        return out

    for reading_div in box.select("div.reading"):
        head = reading_div.find("span")
        if not head:
            continue

        key = norm(head.get_text(" ", strip=True)).lower()

        val = extract_reading_text(reading_div)

        # remove header On/Kun
        val = norm(re.sub(rf"^{re.escape(head.get_text(strip=True))}\s*", "", val))

        if val:
            out.setdefault(key, []).append(val)

    return out


def parse_additional_readings(soup: BeautifulSoup) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    box = find_grow_value(soup, "Additional readings")
    if not box:
        return out

    for reading_div in box.select("div.reading"):
        head = reading_div.find("span")
        if not head:
            continue
        # eg. "Name"
        key = norm(head.get_text(" ", strip=True)).lower()
        full = norm(reading_div.get_text(" ", strip=True))
        val = norm(re.sub(rf"^{re.escape(head.get_text(strip=True))}\s*", "", full))
        if val:
            out.setdefault(key, []).append(val)

    return out


def parse_components(soup: BeautifulSoup) -> str | None:
    box = find_grow_value(soup, "Components")
    if not box:
        return None
    txt = norm(box.get_text(" ", strip=True))
    txt = txt.split("Explore these components visually", 1)[0].strip()
    return txt or None


def parse_kanji_html(html: str) -> Kanji:
    soup = BeautifulSoup(html, "lxml")

    kanji, meaning = parse_h1_means(soup)
    common = parse_common_readings(soup)
    additional = parse_additional_readings(soup)
    components = parse_components(soup)

    return Kanji(
        kanji=kanji,
        meaning=meaning,
        additional=additional,
        raw_common=common,
        raw_components=components,
    )
