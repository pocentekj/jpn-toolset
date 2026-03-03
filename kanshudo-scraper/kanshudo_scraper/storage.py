from pathlib import Path
import sys

import orjson

from .kanji import Kanji


DEFAULT_KANJIS_JSON = Path(__file__).parent.parent.parent / "data" / "kanjis.json"


def _read_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []

    raw = path.read_bytes()
    if not raw.strip():
        return []

    data = orjson.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}")
    return data


def _write_json_array(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(orjson.dumps(items, option=orjson.OPT_INDENT_2))
    tmp.replace(path)


def save_kanji(
    kanji_obj: Kanji,
    path: Path = DEFAULT_KANJIS_JSON,
    *,
    err=sys.stderr,
) -> bool:
    """
    Append/update kanji entry in JSON array file.

    Returns True if saved, False if user declined overwrite.
    """
    if not kanji_obj.kanji:
        print("Cannot save: parsed kanji is missing.", file=err)
        return False

    items = _read_json_array(path)

    idx = next(
        (
            i
            for i, it in enumerate(items)
            if isinstance(it, dict) and it.get("kanji") == kanji_obj.kanji
        ),
        None,
    )

    new_entry = kanji_obj.to_storage_dict()

    if idx is not None:
        # print(
        #     f"Warning: entry for '{kanji_obj.kanji}' already exists in {path}", file=err
        # )
        # ans = input("Overwrite? [y/N]: ").strip().lower()
        # if ans not in {"y", "yes"}:
        #     print("Not overwritten.", file=err)
        #     return False
        items[idx] = new_entry
    else:
        items.append(new_entry)

    _write_json_array(path, items)
    print(f"Saved '{kanji_obj.kanji}' to {path}", file=err)
    return True
