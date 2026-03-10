from .buttons import KanaButtonBase
from .buffer import TextBuffer


class PageBase:
    def _buffer_required(self) -> TextBuffer:
        if not isinstance(self._buffer, TextBuffer):
            raise RuntimeError("TextBuffer is not initialized")
        return self._buffer

    def _on_button_clicked(self, button: KanaButtonBase) -> None:
        buffer = self._buffer_required()
        buffer.append(button.value)
        # This is useful for me as I often work in the terminal
        print(buffer.get_text())

    def set_buffer(self, buffer: TextBuffer) -> None:
        self._buffer = buffer
