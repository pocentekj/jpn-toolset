def kata_to_hira(text: str) -> str:
    """
    Convert katakana to hiragana.
    Leaves non-katakana characters unchanged.
    """
    out: list[str] = []

    for ch in text:
        if "ァ" <= ch <= "ヶ":
            out.append(chr(ord(ch) - 0x60))
        else:
            out.append(ch)

    return "".join(out)


def normalize_kun_reading(reading: str) -> str:
    """
    KANJIDIC style:
      く.る -> くる
      おこな.う -> おこなう
    """
    return reading.replace(".", "")


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def join_or_none(values: list[str], sep: str = " ") -> str | None:
    cleaned = [v.strip() for v in values if v and v.strip()]
    if not cleaned:
        return None
    return sep.join(cleaned)
