# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk  # type: ignore[reportMissingModuleSource]

from .buffer import TextBuffer
from .helpers import resource
from .text_area import TextArea
from .kana_page import KanaPage
from .kanji_page import KanjiPage

APP_NAME = "Kana Keyboard"


@Gtk.Template(filename=resource("main_window.ui"))
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    # main_stack = Gtk.Template.Child()
    kana_page: KanaPage = Gtk.Template.Child()
    kanji_page: KanjiPage = Gtk.Template.Child()
    text_area: TextArea = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._buffer = TextBuffer()
        self.kana_page.set_buffer(self._buffer)
        self.kanji_page.set_buffer(self._buffer)
        self.text_area.set_buffer(self._buffer)


class KanaApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.KanaKeyboard")

    def do_activate(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(resource("style.css"))

        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        window = MainWindow(application=self)
        window.present()
