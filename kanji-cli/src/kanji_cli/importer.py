import time

from .config import KANJIVG_FILE, KANJIDIC_FILE
from .kanji import Kanji
from .parser import (
    load_kanjidic2,
    load_kanjivg_components,
    build_kanji,
)
from .storage import save_kanjis


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


def run() -> int:
    kanjidic = load_kanjidic2(KANJIDIC_FILE)
    components = load_kanjivg_components(KANJIVG_FILE, kanjidic)
    total = len(kanjidic)
    print(f"Started import of {total} kanji...")

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
    result = run()
    end_time = _format_timestamp(time.perf_counter() - start_time)
    print(f"Done in {end_time}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
