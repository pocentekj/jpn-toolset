from importlib.resources import files
import orjson

BASE = files("kana_keyboard")


def resource(name: str) -> str:
    """Load resource file based on name alone"""
    ext = name.rsplit(".", 1)[-1]
    if ext not in ("ui", "css"):
        raise ValueError(name)
    return str(BASE / ext / name)


def json_resource(name: str) -> list | dict:
    return orjson.loads((BASE / "data" / name).read_bytes())
