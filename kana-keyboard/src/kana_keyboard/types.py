from typing import TypedDict


class KanaPair(TypedDict):
    hira: str
    kata: str


class StandardKana(TypedDict):
    hira: str
    kata: str
    dakuten_hira: str | None
    dakuten_kata: str | None
    handakuten_hira: str | None
    handakuten_kata: str | None


StandardKanaEntry = StandardKana | None
SmallKanaEntry = KanaPair | None
YoonKanaEntry = KanaPair | None


class RadicalEntry(TypedDict):
    character: str
    description: str


class ComponentsEntry(TypedDict):
    ids: str
    radicals: list[RadicalEntry]


class ReadingsEntry(TypedDict):
    on: str
    kun: str


class KanjiEntry(TypedDict):
    kanji: str
    readings: ReadingsEntry
    meaning: str
    components: ComponentsEntry
