# This code is mostly AI-generated

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from .kanji import Kanji


KVG_NS = "http://kanjivg.tagaini.net"
KVG = f"{{{KVG_NS}}}"


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _first_english_meaning(rmgroup: ET.Element) -> str | None:
    for meaning in rmgroup.findall("meaning"):
        # KANJIDIC2: meanings without m_lang are English
        if meaning.get("m_lang") is None:
            txt = (meaning.text or "").strip()
            if txt:
                return txt
    return None


def _all_readings(rmgroup: ET.Element, r_type: str) -> list[str]:
    out: list[str] = []
    for reading in rmgroup.findall("reading"):
        if reading.get("r_type") == r_type:
            txt = (reading.text or "").strip()
            if txt:
                out.append(txt)
    return out


@dataclass(slots=True)
class KanjiDicEntry:
    literal: str
    meaning: str | None
    on: list[str]
    kun: list[str]
    nanori: list[str]


def load_kanjidic2(path: str | Path) -> dict[str, KanjiDicEntry]:
    """
    Load KANJIDIC2 into a dict keyed by kanji literal.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    out: dict[str, KanjiDicEntry] = {}

    for char_el in root.findall("character"):
        literal = char_el.findtext("literal")
        if not literal:
            continue

        rm = char_el.find("reading_meaning")
        if rm is None:
            out[literal] = KanjiDicEntry(
                literal=literal,
                meaning=None,
                on=[],
                kun=[],
                nanori=[],
            )
            continue

        rmgroup = rm.find("rmgroup")
        if rmgroup is None:
            out[literal] = KanjiDicEntry(
                literal=literal,
                meaning=None,
                on=[],
                kun=[],
                nanori=[],
            )
            continue

        meaning = _first_english_meaning(rmgroup)
        on = _all_readings(rmgroup, "ja_on")
        kun = _all_readings(rmgroup, "ja_kun")

        nanori: list[str] = []
        for nanori_el in rm.findall("nanori"):
            txt = (nanori_el.text or "").strip()
            if txt:
                nanori.append(txt)

        out[literal] = KanjiDicEntry(
            literal=literal,
            meaning=meaning,
            on=on,
            kun=kun,
            nanori=nanori,
        )

    return out


@dataclass(slots=True)
class KvgNode:
    element: str
    original: str | None
    position: str | None
    children: list["KvgNode"]


def _semantic_children(el: ET.Element) -> list[ET.Element]:
    """
    Return immediate semantic child groups.

    KanjiVG often nests <g> wrappers; we want the first descendant groups
    that actually carry kvg:element.
    """
    out: list[ET.Element] = []

    for child in list(el):
        if _strip_ns(child.tag) != "g":
            continue

        if child.get(f"{KVG}element"):
            out.append(child)
        else:
            out.extend(_semantic_children(child))

    return out


def _build_kvg_node(el: ET.Element) -> KvgNode:
    children = [_build_kvg_node(ch) for ch in _semantic_children(el)]
    return KvgNode(
        element=el.get(f"{KVG}element", ""),
        original=el.get(f"{KVG}original"),
        position=el.get(f"{KVG}position"),
        children=children,
    )


def _find_main_g(kanji_el: ET.Element) -> ET.Element | None:
    """
    Find the main <g kvg:element="..."> for one kanji block.
    """
    for el in kanji_el.iter():
        if _strip_ns(el.tag) != "g":
            continue
        if el.get(f"{KVG}element"):
            return el
    return None


def load_kanjivg(path: str | Path) -> dict[str, KvgNode]:
    """
    Load KanjiVG into a dict keyed by kanji literal.

    Works with the combined XML dump where many <kanji> entries are stored
    in one file.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    out: dict[str, KvgNode] = {}

    for kanji_el in root.iter():
        if _strip_ns(kanji_el.tag) != "kanji":
            continue

        main_g = _find_main_g(kanji_el)
        if main_g is None:
            continue

        literal = main_g.get(f"{KVG}element")
        if not literal:
            continue

        out[literal] = _build_kvg_node(main_g)

    return out


def _meaning_for_component(
    ch: str | None,
    kanjidic: dict[str, KanjiDicEntry],
) -> str:
    if not ch:
        return ""
    entry = kanjidic.get(ch)
    if not entry or not entry.meaning:
        return ""
    return entry.meaning


def _display_component_char(node: KvgNode) -> str:
    """
    Prefer original form when KanjiVG tells us that the visible shape is
    a variant component form.

    Example:
      node.element   = 牜
      node.original  = 牛
      result         = "牜 ( 牛 )"
    """
    if node.original and node.original != node.element:
        return f"{node.element} ( {node.original} )"
    return node.element


def _effective_component_key(node: KvgNode) -> str:
    """
    Which character should we use when looking up meaning?
    Prefer the original/base character if available.
    """
    if node.original:
        return node.original
    return node.element


def _collapse_single_child_chain(node: KvgNode) -> KvgNode:
    """
    KanjiVG sometimes wraps structure in a chain of single-child groups.
    Descend until decomposition becomes meaningful.
    """
    cur = node
    while len(cur.children) == 1:
        cur = cur.children[0]
    return cur


def _infer_ids(children: list[KvgNode]) -> str | None:
    """
    Best-effort IDS inference from KanjiVG position attributes.
    This is intentionally conservative.
    """
    if len(children) < 2:
        return None

    positions = {c.position for c in children if c.position}

    if len(children) == 2:
        if {"left", "right"} <= positions:
            return "⿰"
        if {"top", "bottom"} <= positions:
            return "⿱"
        if {"nyo", "right"} <= positions:
            return "⿺"
        if {"tare", "inside"} <= positions:
            return "⿸"
        if {"kamae", "inside"} <= positions:
            return "⿴"
        return None

    if len(children) == 3:
        if {"left", "right"} <= positions and (
            "center" in positions or "middle" in positions
        ):
            return "⿲"
        if {"top", "bottom"} <= positions and (
            "center" in positions or "middle" in positions
        ):
            return "⿳"
        return None

    return None


def build_raw_components_text(
    kanji: str,
    kanjidic: dict[str, KanjiDicEntry],
    kanjivg: dict[str, KvgNode],
) -> str | None:
    """
    Build a Kanshudo-like single-line components string, simplified.

    Example output:
      "⿰ 耳 ear 戠"
      "⿱ 宀 roof 子 child"
      "耳 ear 戠"
    """
    root = kanjivg.get(kanji)
    if root is None:
        return None

    root = _collapse_single_child_chain(root)
    if not root.children:
        return None

    children = root.children
    ids = _infer_ids(children)

    parts: list[str] = []
    if ids:
        parts.append(ids)

    for child in children:
        shown = _display_component_char(child)
        parts.append(shown)

        desc = _meaning_for_component(_effective_component_key(child), kanjidic)
        if desc:
            parts.append(desc)

    raw = " ".join(parts).strip()
    return raw or None


def build_kanji_from_sources(
    kanji_char: str,
    kanjidic: dict[str, KanjiDicEntry],
    kanjivg: dict[str, KvgNode],
) -> Kanji:
    """
    Build your Kanji dataclass instance from already-loaded sources.
    """
    entry = kanjidic.get(kanji_char)
    if entry is None:
        raise KeyError(f"Kanji {kanji_char!r} not found in KANJIDIC2")

    raw_common: dict[str, list[str]] = {
        "on": entry.on[:],
        "kun": entry.kun[:],
    }

    additional: dict[str, list[str]] = {}
    if entry.nanori:
        additional["name"] = entry.nanori[:]

    raw_components = build_raw_components_text(kanji_char, kanjidic, kanjivg)

    return Kanji(
        kanji=entry.literal,
        meaning=entry.meaning,
        raw_common=raw_common,
        raw_components=raw_components,
        additional=additional,
    )


def build_kanji_from_files(
    kanji_char: str,
    kanjidic2_path: str | Path,
    kanjivg_path: str | Path,
) -> Kanji:
    """
    Convenience wrapper: parse both files and build one Kanji object.

    Fine for testing. For many lookups, load both files once and use
    build_kanji_from_sources().
    """
    kanjidic = load_kanjidic2(kanjidic2_path)
    kanjivg = load_kanjivg(kanjivg_path)
    return build_kanji_from_sources(kanji_char, kanjidic, kanjivg)
