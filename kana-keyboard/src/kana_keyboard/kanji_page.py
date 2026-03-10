# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore[reportMissingModuleSource]

from .buffer import TextBuffer
from .buttons import KanjiButton
from .helpers import resource
from .search import SearchProvider
from .page_base import PageBase


@Gtk.Template(filename=resource("kanji_page.ui"))
class KanjiPage(PageBase, Gtk.Box):
    __gtype_name__ = "KanjiPage"

    results_box = Gtk.Template.Child()
    kanji_search_entry = Gtk.Template.Child()
    reading_search_entry = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._buffer: TextBuffer | None = None
        self._kanjis = SearchProvider()

    def _clear_results_box(self) -> None:
        # GTK 4.12+
        if hasattr(self.results_box, "remove_all"):
            self.results_box.remove_all()
            return

        # Fallback for older GTK / bindings
        child = self.results_box.get_child_at_index(0)
        while child is not None:
            self.results_box.remove(child)
            child = self.results_box.get_child_at_index(0)

    def _update_display(self) -> None:
        kanji_query = self.kanji_search_entry.get_text().strip()
        reading_query = self.reading_search_entry.get_text().strip()

        if kanji_query:
            results = self._kanjis.by_kanji(kanji_query)
        elif reading_query:
            results = self._kanjis.by_readings(reading_query)
        else:
            results = []

        self._clear_results_box()

        for entry in results:
            button = KanjiButton.new_from_entry(entry)
            button.connect("clicked", self._on_button_clicked)
            self.results_box.append(button)

    @Gtk.Template.Callback("on_search_by_kanji")
    def _on_search_by_kanji(self, _entry: Gtk.SearchEntry) -> None:
        self._update_display()

    @Gtk.Template.Callback("on_search_by_readings")
    def _on_search_by_readings(self, _entry: Gtk.SearchEntry) -> None:
        self._update_display()
