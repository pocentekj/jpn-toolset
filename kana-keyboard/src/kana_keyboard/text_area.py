# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore[reportMissingModuleSource]

from .buffer import TextBuffer
from .helpers import resource


@Gtk.Template(filename=resource("text_area.ui"))
class TextArea(Gtk.Box):
    __gtype_name__ = "TextArea"

    scroller = Gtk.Template.Child()
    buffer_textview = Gtk.Template.Child()
    clear_button = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._buffer: TextBuffer | None = None

        gtk_buffer = self.buffer_textview.get_buffer()
        self._gtk_changed_handler_id = gtk_buffer.connect(
            "changed", self._on_textview_changed
        )

    def _buffer_required(self) -> TextBuffer:
        if self._buffer is None:
            raise RuntimeError("TextBuffer not initialized")
        return self._buffer

    def _sync_from_model(self) -> None:
        buffer = self._buffer_required()
        gtk_buffer = self.buffer_textview.get_buffer()

        with gtk_buffer.handler_block(self._gtk_changed_handler_id):
            gtk_buffer.set_text(buffer.get_text())

    def _get_textview_text(self) -> str:
        gtk_buffer = self.buffer_textview.get_buffer()
        start = gtk_buffer.get_start_iter()
        end = gtk_buffer.get_end_iter()
        return gtk_buffer.get_text(start, end, True)

    def _on_model_changed(self, *_args) -> None:
        self._sync_from_model()

    def _on_textview_changed(self, _gtk_buffer: Gtk.TextBuffer) -> None:
        buffer = self._buffer_required()
        buffer.set_text(self._get_textview_text())

    @Gtk.Template.Callback("on_clear_clicked")
    def _on_clear(self, _button: Gtk.Button) -> None:
        buffer = self._buffer_required()
        buffer.clear()

    def set_buffer(self, buffer: TextBuffer) -> None:
        self._buffer = buffer
        self._buffer.connect("changed", self._on_model_changed)
        self._sync_from_model()
