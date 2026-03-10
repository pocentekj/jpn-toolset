# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject  # type: ignore[reportMissingModuleSource]


class TextBuffer(GObject.Object):
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, text: str = "") -> None:
        super().__init__()
        self._text = text

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        if text == self._text:
            return
        self._text = text
        self.emit("changed")

    def append(self, text: str) -> None:
        self._text += text
        self.emit("changed")

    def backspace(self) -> None:
        if self._text:
            self._text = self._text[:-1]

    def replace_last(self, text: str) -> None:
        if self._text:
            self._text = self._text[:-1] + text

    def clear(self) -> None:
        self._text = ""
        self.emit("changed")

    def is_empty(self) -> bool:
        return self._text == ""

    def last_char(self) -> str | None:
        return self._text[-1] if self._text else None

    def __len__(self) -> int:
        return len(self._text)

    def __repr__(self) -> str:
        return f"TextBuffer({self._text!r})"
