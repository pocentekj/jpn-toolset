# /usr/bin/env python3
from kanji_catalogue import KanjiApp


def main():
    app = KanjiApp()
    raise SystemExit(app.run(None))


if __name__ == "__main__":
    main()
