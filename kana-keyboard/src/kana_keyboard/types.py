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


class KanjiEntry(TypedDict):
    kanji: str
    on_readings: str | None
    kun_readings: str | None
    meaning: str
