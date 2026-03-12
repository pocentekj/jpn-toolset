import sys
import argparse
from typing import IO
from .db import search_entries


def run(term: str, use_color: bool, out_file: IO = sys.stdout):
    results = search_entries(term)

    if not results:
        return 2

    for dict_entry in results:
        if use_color:
            print(dict_entry.format_for(term), file=out_file)
        else:
            print(dict_entry, file=out_file)

    return 0


def main() -> int:  # noqa
    parser = argparse.ArgumentParser(prog="mdict")
    parser.add_argument("term", help="search term")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable colored output",
    )
    args = parser.parse_args()
    return run(args.term, not args.no_color)


if __name__ == "__main__":  # noqa
    raise SystemExit(main())
