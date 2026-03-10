from dataclasses import InitVar, dataclass, field

import orjson

IDC_CHARS = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")


def _is_component_start_token(tok: str) -> bool:
    """Best-effort: detect a token that begins a new component (radical/part)."""
    if not tok:
        return False
    if tok in IDC_CHARS:
        return True
    # Kanshudo component tokens are usually single-character parts (incl. radicals).
    if len(tok) != 1:
        return False

    cp = ord(tok)
    # CJK Unified / Extension A
    if 0x3400 <= cp <= 0x9FFF:
        return True
    # CJK Compatibility Ideographs
    if 0xF900 <= cp <= 0xFAFF:
        return True
    # CJK Radicals Supplement / Kangxi radicals / etc.
    if 0x2E80 <= cp <= 0x2FD5:
        return True

    # Common “variant radical” codepoints used in dictionaries
    if tok in {
        "⻏",
        "⻖",
        "⺉",
        "⺾",
        "⻌",
        "⺌",
        "⺡",
        "⺗",
        "⺥",
        "⺮",
        "⺹",
        "⺭",
        "⺲",
        "⺳",
        "⻂",
    }:
        return True

    return False


@dataclass(slots=True)
class Radical:
    character: str
    description: str


@dataclass(slots=True)
class Components:
    ids: str | None
    radicals: list[Radical] = field(default_factory=list)


@dataclass(slots=True)
class Readings:
    on: str = ""
    kun: str = ""


def parse_components_text(text: str) -> Components:
    """Parse Kanshudo's single-line components payload.

    Example input:
      "⿰ 牜 ( 牛 ) cow 勿 not"

    Output radicals keep the 'character' as e.g. "牜 ( 牛 )" and description as "cow".
    """

    tokens = [t for t in text.strip().split() if t]
    if not tokens:
        return Components(ids=None, radicals=[])

    ids = tokens[0]
    i = 1
    radicals: list[Radical] = []

    while i < len(tokens):
        ch = tokens[i]
        i += 1

        # Variant form: "⻏ ( 邑 )" etc.
        if i + 2 < len(tokens) and tokens[i] == "(" and tokens[i + 2] == ")":
            ch = f"{ch} ( {tokens[i + 1]} )"
            i += 3

        desc_parts: list[str] = []
        while i < len(tokens) and not _is_component_start_token(tokens[i]):
            desc_parts.append(tokens[i])
            i += 1

        radicals.append(Radical(character=ch, description=" ".join(desc_parts).strip()))

    return Components(ids=ids, radicals=radicals)


@dataclass
class Kanji:
    kanji: str | None
    meaning: str | None

    raw_common: InitVar[dict[str, list[str]]]
    raw_components: InitVar[str | None]

    readings: Readings = field(init=False)
    components: Components = field(init=False)

    additional: dict[str, list[str]] = field(default_factory=dict)

    _components_text: str | None = field(init=False, repr=False, default=None)

    def __post_init__(
        self, raw_common: dict[str, list[str]], raw_components: str | None
    ) -> None:
        # Normalize readings once (Common readings)
        readings = {
            "on": " ".join(raw_common.get("on", [])).strip(),
            "kun": " ".join(raw_common.get("kun", [])).strip(),
        }

        # Kanshudo sometimes puts readings only under "Additional readings" (e.g. 雑 has kun here).
        for group in readings.keys():
            if group not in self.additional:
                continue
            if readings[group]:
                readings[group] += "; "
            readings[group] += " ".join(self.additional.pop(group)).strip()

        self.readings = Readings(**readings)

        # Parse components once (and keep original text for rendering)
        self._components_text = raw_components
        if raw_components:
            self.components = parse_components_text(raw_components)
        else:
            self.components = Components(ids=None, radicals=[])

    # -------------------------
    # Renderers
    # -------------------------
    def format_pretty(self) -> str:
        lines: list[str] = []
        if self.kanji and self.meaning:
            lines.append(f"{self.kanji} means '{self.meaning}'")

        lines.append("")

        if self.readings.on:
            lines.append(f"on:   {self.readings.on}")
        if self.readings.kun:
            lines.append(f"kun:  {self.readings.kun}")

        if self.additional:
            if "name" in self.additional:
                lines.append(f"name: {' | '.join(self.additional['name'])}")
            for k, vals in self.additional.items():
                if k == "name":
                    continue
                lines.append(f"{k}: {' | '.join(vals)}")

        lines.append("")
        if self._components_text:
            lines.append(f"Components: {self._components_text}")

        return "\n".join(lines).rstrip() + "\n"

    def format_markdown(self) -> str:
        head = ""
        if self.kanji and self.meaning:
            head = f"### {self.kanji} means '{self.meaning}'\n\n"

        table = (
            "| | Reading |\n"
            "| ----------- | ----------- |\n"
            f"on | {self.readings.on} |\n"
            f"kun | {self.readings.kun} |\n\n"
        )

        comp = ""
        if self._components_text:
            comp = f"Components: {self._components_text}\n"

        return head + table + comp

    def to_storage_dict(self) -> dict:
        return {
            "kanji": self.kanji,
            "readings": {
                "on": self.readings.on,
                "kun": self.readings.kun,
            },
            "meaning": self.meaning,
            "components": {
                "ids": self.components.ids,
                "radicals": [
                    {"character": r.character, "description": r.description}
                    for r in self.components.radicals
                ],
            },
        }

    def format_json(self) -> str:
        return orjson.dumps(self.to_storage_dict()).decode("utf-8")
