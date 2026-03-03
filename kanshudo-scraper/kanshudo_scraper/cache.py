from pathlib import Path
from urllib.parse import quote

CACHE_DIRECTORY = Path(__file__).parent.parent / ".cache"


def _cache_path_html(kanji: str) -> Path:
    safe = quote(kanji, safe="")
    return CACHE_DIRECTORY / f"{safe}.html"


def has_html(kanji: str) -> bool:
    return _cache_path_html(kanji).exists()


def load_html(kanji: str) -> str | None:
    path = _cache_path_html(kanji)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def save_html(kanji: str, html: str) -> Path:
    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    path = _cache_path_html(kanji)
    path.write_text(html, encoding="utf-8")
    return path
