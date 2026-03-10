# ruff: noqa: E402
import gi
from typing import Self

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore[reportMissingModuleSource]

from .types import KanjiEntry, StandardKana, KanaPair


class KanaButtonBase(Gtk.Button):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.add_css_class("kana-key")
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_label(label)

    @property
    def value(self) -> str:
        return self.get_label() or ""


class KanjiButton(KanaButtonBase):
    def __init__(self, label: str) -> None:
        super().__init__(label)

    @classmethod
    def new_from_entry(cls, entry: KanjiEntry) -> Self:
        button = cls(entry["kanji"])

        readings = entry["readings"]
        on = readings.get("on", "")
        kun = readings.get("kun", "")
        meaning = entry.get("meaning", "")

        tooltip_parts: list[str] = []

        if on:
            tooltip_parts.append(f"On: {on}")
        if kun:
            tooltip_parts.append(f"Kun: {kun}")
        if meaning:
            tooltip_parts.append(f"Meaning: {meaning}")

        button.set_tooltip_text("\n".join(tooltip_parts))

        return button


class KanaModeButton(KanaButtonBase):
    """Switchable buttons: kata/hira, dakuten/handakuten."""

    def __init__(self, label: str) -> None:
        super().__init__(label=label)
        self._kata = False
        self._dakuten = False
        self._handakuten = False

    def _update_label(self) -> None:
        raise NotImplementedError

    def set_mode(
        self,
        *,
        kata: bool | None = None,
        dakuten: bool | None = None,
        handakuten: bool | None = None,
    ) -> None:
        if kata is not None:
            self._kata = kata

        if dakuten is not None:
            self._dakuten = dakuten

        if handakuten is not None:
            self._handakuten = handakuten

        self._update_label()


class KanaButtonStd(KanaModeButton):
    """Standard kana"""

    _entry: StandardKana

    def __init__(self, entry: StandardKana) -> None:
        super().__init__(label=entry["hira"])
        self._entry = entry

    def _update_label(self) -> None:
        base_key = "kata" if self._kata else "hira"

        if self._handakuten:
            key = "handakuten_kata" if self._kata else "handakuten_hira"
            label = self._entry[key]
            self.set_label(label if label is not None else self._entry[base_key])
            return

        if self._dakuten:
            key = "dakuten_kata" if self._kata else "dakuten_hira"
            label = self._entry[key]
            self.set_label(label if label is not None else self._entry[base_key])
            return

        self.set_label(self._entry[base_key])


class KanaButtonPair(KanaModeButton):
    """Base class for small/yoon kana"""

    _entry: KanaPair

    def __init__(self, entry: KanaPair) -> None:
        super().__init__(label=entry["hira"])
        self._entry = entry

    def _update_label(self) -> None:
        self.set_label(self._entry["kata"] if self._kata else self._entry["hira"])


class KanaButtonPunct(KanaButtonBase):
    """Punctuation"""

    def __init__(self, entry: str) -> None:
        super().__init__(label=entry)
