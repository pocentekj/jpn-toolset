import sys
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Literal

from .parser import build_kanji_from_files
from .storage import save_kanji

KANJIDIC_FILE = Path(__file__).parent.parent.parent / "data" / "kanjidic2.xml"

KANJIVG_FILE = Path(__file__).parent.parent.parent / "data" / "kanjivg-20220427.xml"


@dataclass
class AppConfig:
    kanji: str
    output_format: Literal["pretty", "markdown", "json"]
    save: bool
    out_file: IO = sys.stdout
    err_file: IO = sys.stderr


def run(config: AppConfig) -> int:
    kanji = build_kanji_from_files(
        kanji_char=config.kanji,
        kanjidic2_path=KANJIDIC_FILE,
        kanjivg_path=KANJIVG_FILE,
    )

    print(getattr(kanji, f"format_{config.output_format}")(), file=config.out_file)

    if config.save:
        save_kanji(kanji)

    return 0


def main() -> int:  # noqa
    import argparse

    parser = argparse.ArgumentParser(prog="kanshudo")
    parser.add_argument("kanji")
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["pretty", "markdown", "json"],
        default="pretty",
        help="Output format (default: pretty)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Append parsed kanji to data/kanjis.json",
    )
    args = parser.parse_args()

    cfg = AppConfig(
        kanji=args.kanji,
        output_format=args.output_format,
        save=args.save,
    )

    return run(cfg)


if __name__ == "__main__":  # noqa
    raise SystemExit(main())
