import sys
import argparse
from dataclasses import dataclass
from typing import IO

from .db import search_entries


@dataclass
class AppConfig:
    # Search by dict word or reading (hiragana)
    term: str

    # Highlight search term in output
    use_color: bool

    # LIMIT for search query
    max_results: int

    out_file: IO = sys.stdout
    err_file: IO = sys.stderr


def run(config: AppConfig):
    results = search_entries(config.term, config.max_results)

    if not results:
        print("No results", file=config.err_file)
        return 2

    for dict_entry in results:
        if config.use_color:
            print(dict_entry.format_for(config.term), file=config.out_file)
        else:
            print(dict_entry, file=config.out_file)

    return 0


def main() -> int:  # noqa
    parser = argparse.ArgumentParser(prog="mdict")
    parser.add_argument("term", help="search term")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable colored output",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=50,
        dest="max_results",
        help="max results to be displayed",
    )

    args = parser.parse_args()

    return run(
        AppConfig(
            term=args.term,
            use_color=not args.no_color,
            max_results=args.max_results,
        )
    )


if __name__ == "__main__":  # noqa
    raise SystemExit(main())
