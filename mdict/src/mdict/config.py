import os
from pathlib import Path

DICT_PATH = Path(__file__).parent / "data" / "JMdict.xml"

DB_PATH = Path(os.environ.get("HOME", ".")) / ".local" / "share" / "mdict.sqlite"
