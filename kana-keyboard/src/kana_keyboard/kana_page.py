# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore[reportMissingModuleSource]

from typing import cast

from .buttons import (
    KanaButtonBase,
    KanaButtonPair,
    KanaButtonStd,
    KanaModeButton,
    KanaButtonPunct,
)
from .buffer import TextBuffer
from .helpers import resource, json_resource
from .page_base import PageBase
from .types import (
    StandardKanaEntry,
    SmallKanaEntry,
    YoonKanaEntry,
)

StandardKanaTable = list[list[StandardKanaEntry]]
SmallKanaTable = list[list[SmallKanaEntry]]
YoonKanaTable = list[list[YoonKanaEntry]]

KanaTable = StandardKanaTable | SmallKanaTable | YoonKanaTable | list[list[str]]

STANDARD_KANA = cast(StandardKanaTable, json_resource("standard.json"))

SMALL_KANA = cast(SmallKanaTable, json_resource("small.json"))

YOON_KANA = cast(YoonKanaTable, json_resource("yoon.json"))

PUNCTUATION = [
    ["。", "、", "・", "「", "」", "『"],
    ["』", "ー", "〜", "…", "？", "！"],
]


@Gtk.Template(filename=resource("kana_page.ui"))
class KanaPage(PageBase, Gtk.Box):
    __gtype_name__ = "KanaPage"

    standard_grid = Gtk.Template.Child()
    small_grid = Gtk.Template.Child()
    yoon_grid = Gtk.Template.Child()
    punctuation_grid = Gtk.Template.Child()

    hiragana_button = Gtk.Template.Child()
    katakana_button = Gtk.Template.Child()

    dakuten_button = Gtk.Template.Child()
    handakuten_button = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._buffer: TextBuffer | None = None
        self._buttons: list[KanaButtonBase] = []
        self._build_keyboard()

    def _set_keyboard_mode(
        self,
        *,
        kata: bool | None = None,
        dakuten: bool | None = None,
        handakuten: bool | None = None,
    ) -> None:
        for btn in self._buttons:
            if isinstance(btn, KanaModeButton):
                btn.set_mode(
                    kata=kata,
                    dakuten=dakuten,
                    handakuten=handakuten,
                )

    def _build_keyboard(self) -> None:
        items = (
            (self.standard_grid, STANDARD_KANA, KanaButtonStd),
            (self.small_grid, SMALL_KANA, KanaButtonPair),
            (self.yoon_grid, YOON_KANA, KanaButtonPair),
            (self.punctuation_grid, PUNCTUATION, KanaButtonPunct),
        )

        for grid, table, cls in items:
            for row_index, row in enumerate(table):
                for col_index, entry in enumerate(row):
                    if entry is None:
                        continue
                    button = cls(entry)  # type: ignore[reportArgumentType]
                    grid.attach(button, col_index, row_index, 1, 1)
                    self._buttons.append(button)
                    button.connect("clicked", self._on_button_clicked)

    @Gtk.Template.Callback("on_katakana_toggled")
    def _on_katakana_toggled(self, button: Gtk.ToggleButton) -> None:
        self._set_keyboard_mode(kata=button.get_active())

    @Gtk.Template.Callback("on_hiragana_toggled")
    def _on_hiragana_toggled(self, button: Gtk.ToggleButton) -> None:
        if button.get_active():
            self._set_keyboard_mode(kata=False)

    @Gtk.Template.Callback("on_dakuten_toggled")
    def _on_dakuten_toggled(self, button: Gtk.ToggleButton) -> None:
        active = button.get_active()

        if active and self.handakuten_button.get_active():
            self.handakuten_button.set_active(False)

        self._set_keyboard_mode(dakuten=active)

    @Gtk.Template.Callback("on_handakuten_toggled")
    def _on_handakuten_toggled(self, button: Gtk.ToggleButton) -> None:
        active = button.get_active()

        if active and self.dakuten_button.get_active():
            self.dakuten_button.set_active(False)

        self._set_keyboard_mode(handakuten=active)
