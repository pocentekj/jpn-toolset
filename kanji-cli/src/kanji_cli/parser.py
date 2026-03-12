# This file is mostly AI-generated

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from .helpers import (
    kata_to_hira,
    normalize_kun_reading,
    strip_ns,
    join_or_none,
)
from .kanji import Kanji


KVG_NS = "http://kanjivg.tagaini.net"
KVG = f"{{{KVG_NS}}}"


@dataclass(slots=True)
class KanjiDicEntry:
    kanji: str
    meanings: list[str]
    on_readings: list[str]
    kun_readings: list[str]
    name_readings: list[str]
    freq: int


def load_kanjidic2(path: str | Path) -> dict[str, KanjiDicEntry]:
    """
    Load KANJIDIC2 into a dict keyed by kanji.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    out: dict[str, KanjiDicEntry] = {}

    for char_el in root.findall("character"):
        kanji = char_el.findtext("literal")
        if not kanji:
            continue

        meanings: list[str] = []
        on_readings: list[str] = []
        kun_readings: list[str] = []
        name_readings: list[str] = []

        freq_text = char_el.findtext("misc/freq")
        freq = int(freq_text) if freq_text else 999999

        reading_meaning = char_el.find("reading_meaning")
        if reading_meaning is not None:
            rmgroup = reading_meaning.find("rmgroup")
            if rmgroup is not None:
                for reading_el in rmgroup.findall("reading"):
                    r_type = reading_el.get("r_type")
                    value = (reading_el.text or "").strip()
                    if not value:
                        continue

                    if r_type == "ja_on":
                        on_readings.append(value)
                    elif r_type == "ja_kun":
                        kun_readings.append(normalize_kun_reading(value))

                for meaning_el in rmgroup.findall("meaning"):
                    # English meanings in KANJIDIC2 usually have no m_lang
                    if meaning_el.get("m_lang") is None:
                        value = (meaning_el.text or "").strip()
                        if value:
                            meanings.append(value)

            for nanori_el in reading_meaning.findall("nanori"):
                value = (nanori_el.text or "").strip()
                if value:
                    name_readings.append(value)

        out[kanji] = KanjiDicEntry(
            kanji=kanji,
            meanings=meanings,
            on_readings=on_readings,
            kun_readings=kun_readings,
            name_readings=name_readings,
            freq=freq,
        )

    return out


def semantic_children(el: ET.Element) -> list[ET.Element]:
    """
    Return descendant <g> nodes that carry semantic kvg:element information.
    """
    out: list[ET.Element] = []

    for child in list(el):
        if strip_ns(child.tag) != "g":
            continue

        if child.get(f"{KVG}element"):
            out.append(child)
        else:
            out.extend(semantic_children(child))

    return out


def find_main_g(kanji_el: ET.Element) -> ET.Element | None:
    """
    Find the main semantic group for one kanji entry.
    """
    for el in kanji_el.iter():
        if strip_ns(el.tag) != "g":
            continue
        if el.get(f"{KVG}element"):
            return el
    return None


def component_gloss(
    element: str,
    original: str | None,
    kanjidic: dict[str, KanjiDicEntry],
) -> str | None:
    """
    Return a short English gloss for a component.

    Prefer original/base form when available, e.g.:
      ⺅ ( 人 ) -> gloss from 人
    Otherwise use the component element itself.
    """
    lookup = original if original and original != element else element
    entry = kanjidic.get(lookup)
    if entry is None:
        return None

    # take first English meaning as a compact gloss
    if not entry.meanings:
        return None

    return entry.meanings[0]


def collect_top_components(
    main_g: ET.Element,
    kanjidic: dict[str, KanjiDicEntry],
) -> list[str]:
    """
    Collect top-level components for a kanji, without IDS.

    Output examples:
        耳 ear
        ⺅ ( 人 ) person
    """
    components: list[str] = []

    for child in semantic_children(main_g):
        element = child.get(f"{KVG}element")
        if not element:
            continue

        original = child.get(f"{KVG}original")

        if original and original != element:
            label = f"{element} ( {original} )"
        else:
            label = element

        gloss = component_gloss(element, original, kanjidic)
        if gloss:
            components.append(f"{label} {gloss}")
        else:
            components.append(label)

    return components


def load_kanjivg_components(
    path: str | Path,
    kanjidic: dict[str, KanjiDicEntry],
) -> dict[str, list[str]]:
    """
    Load KanjiVG and map:
        kanji -> ["component gloss", ...]
    """
    tree = ET.parse(path)
    root = tree.getroot()

    out: dict[str, list[str]] = {}

    for kanji_el in root.iter():
        if strip_ns(kanji_el.tag) != "kanji":
            continue

        main_g = find_main_g(kanji_el)
        if main_g is None:
            continue

        kanji = main_g.get(f"{KVG}element")
        if not kanji:
            continue

        components = collect_top_components(main_g, kanjidic)
        out[kanji] = components

    return out


def build_kanji(
    kanji_char: str,
    kanjidic: dict[str, KanjiDicEntry],
    kanjivg_components: dict[str, list[str]],
) -> Kanji:
    entry = kanjidic.get(kanji_char)
    if entry is None:
        raise KeyError(f"Kanji not found in KANJIDIC2: {kanji_char!r}")

    on_readings = join_or_none(entry.on_readings)
    on_readings_norm = kata_to_hira(on_readings) if on_readings else None
    kun_readings = join_or_none(entry.kun_readings)
    name_readings = join_or_none(entry.name_readings)
    meaning = join_or_none(entry.meanings, sep="; ")

    raw_components = kanjivg_components.get(kanji_char, [])
    components = join_or_none(raw_components)

    return Kanji(
        kanji=entry.kanji,
        meaning=meaning,
        on_readings=on_readings,
        on_readings_norm=on_readings_norm,
        kun_readings=kun_readings,
        name_readings=name_readings,
        components=components,
        freq=entry.freq,
    )


def build_kanji_from_files(
    kanji_char: str,
    kanjidic2_path: str | Path,
    kanjivg_path: str | Path,
) -> Kanji:
    """
    Convenience helper for one-off tests.
    For bulk import, load both sources once and reuse them.
    """
    kanjidic = load_kanjidic2(kanjidic2_path)
    kanjivg_components = load_kanjivg_components(kanjivg_path, kanjidic)
    return build_kanji(kanji_char, kanjidic, kanjivg_components)
