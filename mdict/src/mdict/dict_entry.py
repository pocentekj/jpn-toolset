from dataclasses import dataclass


@dataclass
class DictEntry:
    headword: str
    reading: str | None
    gloss: str

    def __str__(self) -> str:
        reading = f" ({self.reading})" if self.reading else ""
        return f"{self.headword}{reading}: {self.gloss}"

    def format_for(self, search_term: str) -> str:
        return str(self).replace(search_term, f"\x1b[31m{search_term}\x1b[0m")
