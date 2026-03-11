import time

from .config import KANJIVG_FILE, KANJIDIC_FILE
from .kanji import Kanji
from .parser import (
    load_kanjidic2,
    load_kanjivg_components,
    build_kanji,
)
from .storage import save_kanjis


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"


def run() -> int:
    print("Loading KANJIDIC2...")
    kanjidic = load_kanjidic2(KANJIDIC_FILE)

    print("Loading KanjiVG components...")
    components = load_kanjivg_components(KANJIVG_FILE, kanjidic)

    total = len(kanjidic)
    print(f"Importing {total} kanji...")

    count = 0

    kanjis: list[Kanji] = []

    for kanji_char in kanjidic:
        entry = build_kanji(kanji_char, kanjidic, components)
        kanjis.append(entry)
        count += 1

        if count % 500 == 0:
            save_kanjis(kanjis)
            kanjis = []
            print(f"{count}/{total}")

    if kanjis:
        save_kanjis(kanjis)

    print(f"Imported {count} kanji")

    return 0


def main() -> int:
    start_time = time.perf_counter()

    print("Starting import...")
    result = run()

    end_time = format_timestamp(time.perf_counter() - start_time)
    print(f"Done in {end_time}")

    return result


if __name__ == "__main__":
    raise SystemExit(main())
