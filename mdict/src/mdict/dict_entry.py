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
        text = str(self)

        if not search_term:
            return text

        red = "\x1b[31m"
        reset = "\x1b[0m"

        return text.replace(search_term, f"{red}{search_term}{reset}")
