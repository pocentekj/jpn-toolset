import re


_ws = re.compile(r"\s+")


def is_blank(line: str) -> bool:
    return line.strip() == ""


def split_kv(line: str) -> tuple[str, str] | None:
    """
    Split 'key: value' into (key, value) with whitespace trimmed.
    Returns None if ':' is missing.
    """
    if ":" not in line:
        return None
    k, v = line.split(":", 1)
    return k.strip(), v.strip()


def norm(s: str) -> str:
    # normalize whitespace + NBSP
    return _ws.sub(" ", s.replace("\xa0", " ")).strip()
