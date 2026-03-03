import sys
from dataclasses import dataclass
from urllib.parse import quote
from typing import IO, Literal

import requests

from kanshudo_scraper.cache import load_html, save_html
from kanshudo_scraper.parser import parse_kanji_html
from kanshudo_scraper.storage import save_kanji

BASE_URL = "https://www.kanshudo.com/kanji/"

UA_FIREFOX = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


@dataclass
class AppConfig:
    kanji: str
    output_format: Literal["pretty", "markdown", "json"]
    save: bool


def main(config: AppConfig, out: IO = sys.stdout, err: IO = sys.stderr) -> int:
    html = load_html(config.kanji)

    if html is None:
        url = BASE_URL + quote(config.kanji)
        headers = {"User-Agent": UA_FIREFOX}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Invalid server response: {response.status_code}", file=err)
            return 1

        html = response.text
        save_html(config.kanji, html)

    kanji = parse_kanji_html(html)

    print(getattr(kanji, f"format_{config.output_format}")(), file=out)

    if config.save:
        save_kanji(kanji, err=err)

    return 0


if __name__ == "__main__":  # noqa
    import argparse

    parser = argparse.ArgumentParser(prog="kanshudo")
    parser.add_argument("kanji")
    parser.add_argument(
        "-f", "--format",
        dest="output_format",
        choices=["pretty", "markdown", "json"],
        default="pretty",
        help="Output format (default: pretty)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Append parsed kanji to data/kanjis.json (asks before overwrite)",
    )
    args = parser.parse_args()

    cfg = AppConfig(
        kanji=args.kanji,
        output_format=args.output_format,
        save=args.save,
    )

    raise SystemExit(main(cfg))
