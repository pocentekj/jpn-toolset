# ruff: noqa: E402
#
# Kana/Kanji keyboard prototyped in PyGTK.
# Note: This code is mostly AI-generated
#
import gi
import pathlib
import orjson

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Gdk, GLib  # type: ignore[reportMissingModuleSource]

APP_ID = "pl.chester.kanji_catalogue"

ICON_PATH = pathlib.Path(__file__).parent.parent / "icon.png"

KANJIS_JSON_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "kanjis.json"

DAKUTEN = {
    "か": "が",
    "き": "ぎ",
    "く": "ぐ",
    "け": "げ",
    "こ": "ご",
    "さ": "ざ",
    "し": "じ",
    "す": "ず",
    "せ": "ぜ",
    "そ": "ぞ",
    "た": "だ",
    "ち": "ぢ",
    "つ": "づ",
    "て": "で",
    "と": "ど",
    "は": "ば",
    "ひ": "び",
    "ふ": "ぶ",
    "へ": "べ",
    "ほ": "ぼ",
}

HANDAKUTEN = {"は": "ぱ", "ひ": "ぴ", "ふ": "ぷ", "へ": "ぺ", "ほ": "ぽ"}


def load_kanjis(path: pathlib.Path = KANJIS_JSON_PATH) -> list[dict]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    if not raw.strip():
        return []
    data = orjson.loads(raw)
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def ulen(s: str) -> int:
    """ Count codepoints (OK for Japanese) """
    return len(s)


class KanjiPad(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(title="Kanji Catalogue", *args, **kwargs)
        self.set_default_size(980, 720)
        self.set_icon_from_file(str(ICON_PATH))

        settings = Gtk.Settings.get_default()
        if settings is not None:
            settings.set_property("gtk-application-prefer-dark-theme", True)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.set_border_width(12)
        self.add(outer)

        self.items = load_kanjis()

        # --- Header: counter ---
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        outer.pack_start(header, False, False, 0)

        title = Gtk.Label()
        title.set_markup("<b>Kanji Pad</b>")
        title.set_xalign(0)
        header.pack_start(title, True, True, 0)

        self.count_lbl = Gtk.Label(label="0 znaków")
        header.pack_end(self.count_lbl, False, False, 0)

        # --- TextView + toolbar (common for both tabs) ---
        self.buf = Gtk.TextBuffer()
        self.buf.connect("changed", self.on_buffer_changed)

        tv = Gtk.TextView(buffer=self.buf)
        tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        tv.set_monospace(False)

        sc = Gtk.ScrolledWindow()
        sc.set_hexpand(True)
        sc.set_vexpand(False)
        sc.set_min_content_height(160)
        sc.add(tv)
        outer.pack_start(sc, False, False, 0)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        outer.pack_start(toolbar, False, False, 0)

        btn_copy = Gtk.Button(label="Kopiuj")
        btn_copy.connect("clicked", self.on_copy)
        toolbar.pack_start(btn_copy, False, False, 0)

        btn_space = Gtk.Button(label="Spacja")
        btn_space.connect("clicked", lambda *_: self.insert_text(" "))
        toolbar.pack_start(btn_space, False, False, 0)

        btn_nl = Gtk.Button(label="Nowa linia")
        btn_nl.connect("clicked", lambda *_: self.insert_text("\n"))
        toolbar.pack_start(btn_nl, False, False, 0)

        btn_bs = Gtk.Button(label="Backspace")
        btn_bs.connect("clicked", self.on_backspace)
        toolbar.pack_start(btn_bs, False, False, 0)

        btn_cl = Gtk.Button(label="Wyczyść")
        btn_cl.connect("clicked", self.on_clear)
        toolbar.pack_start(btn_cl, False, False, 0)

        # --- Notebook ---
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        outer.pack_start(self.notebook, True, True, 0)

        # ========== TAB 1: Kanji ==========
        kanji_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # --- Filters (Kanji) ---
        filt = Gtk.Grid(column_spacing=8, row_spacing=8)
        kanji_page.pack_start(filt, False, False, 0)

        self.q_yomi = Gtk.Entry()
        self.q_yomi.set_placeholder_text("よみ (np. せかい / じかん / ひと)")
        self.q_yomi.connect("changed", lambda *_: self.refresh())

        self.q_kanji = Gtk.Entry()
        self.q_kanji.set_placeholder_text("kanji (np. 世 / 界 / 間)")
        self.q_kanji.connect("changed", lambda *_: self.refresh())

        self.q_tag = Gtk.Entry()
        self.q_tag.set_placeholder_text("tag (np. podstawowe / czas / kierunki)")
        self.q_tag.connect("changed", lambda *_: self.refresh())

        filt.attach(self.q_yomi, 0, 0, 1, 1)
        filt.attach(self.q_kanji, 1, 0, 1, 1)
        filt.attach(self.q_tag, 2, 0, 1, 1)

        # --- Tile Grid (FlowBox) ---
        self.flow = Gtk.FlowBox()
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_max_children_per_line(8)
        self.flow.set_row_spacing(8)
        self.flow.set_column_spacing(8)

        sc2 = Gtk.ScrolledWindow()
        sc2.set_hexpand(True)
        sc2.set_vexpand(True)
        sc2.add(self.flow)
        kanji_page.pack_start(sc2, True, True, 0)

        self.notebook.append_page(kanji_page, Gtk.Label(label="Kanji"))

        # ========== TAB 2: Kana ==========
        kana_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        if hasattr(self, "build_kana_keyboard"):
            kana_page.pack_start(self.build_kana_keyboard(), False, False, 0)
        else:
            kana_page.pack_start(
                Gtk.Label(label="TODO: Kana keyboard"), False, False, 0
            )

        self.notebook.append_page(kana_page, Gtk.Label(label="かな"))

        # --- render ---
        self.refresh()

    # ---------- Text ops ----------
    def get_text(self) -> str:
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        return self.buf.get_text(start, end, True)

    def set_text(self, s: str) -> None:
        self.buf.set_text(s)

    def insert_text(self, s: str) -> None:
        it = self.buf.get_end_iter()
        self.buf.insert(it, s)

    def on_backspace(self, *_):
        txt = self.get_text()
        if not txt:
            return
        # remove last character (codepoint)
        self.set_text(txt[:-1])

    def on_clear(self, *_):
        self.set_text("")

    def on_copy(self, *_):
        txt = self.get_text()
        cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        cb.set_text(txt, -1)
        cb.store()

    def on_buffer_changed(self, *_):
        self.count_lbl.set_text(f"{ulen(self.get_text())} chars")

    # ---------- Filtering / UI ----------
    def matches(self, item) -> bool:
        a = self.q_yomi.get_text().strip()
        b = self.q_kanji.get_text().strip()
        c = self.q_tag.get_text().strip()

        kan = (item.get("kanji") or "")
        readings = item.get("readings") or {}
        on = (readings.get("on") or "")
        kun = (readings.get("kun") or "")

        # "よみ" -> search 'kun' and 'on'
        if a and (a not in on) and (a not in kun):
            return False
        if b and b not in kan:
            return False
        # TODO: obsolete
        if c:
            tag_val = item.get("t") or item.get("tag") or ""
            if c not in tag_val:
                return False
            return False
        return True

    def make_tile(self, item: dict) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_border_width(8)

        kan = item.get("kanji", "") or ""
        readings = item.get("readings") or {}
        on = (readings.get("on") or "").strip()
        kun = (readings.get("kun") or "").strip()
        yomi = " / ".join([x for x in (on, kun) if x])
        meaning = (item.get("meaning") or "").strip()

        lbl_k = Gtk.Label(label=kan)
        lbl_k.set_xalign(0.5)
        lbl_k.set_text(kan)
        lbl_k.set_name("kanji-big")

        lbl_y = Gtk.Label(label=yomi)
        lbl_y.set_xalign(0.5)

        lbl_m = Gtk.Label(label=meaning)
        lbl_m.set_xalign(0.5)
        lbl_m.set_line_wrap(True)
        lbl_m.set_max_width_chars(14)

        box.pack_start(lbl_k, False, False, 0)
        box.pack_start(lbl_y, False, False, 0)
        box.pack_start(lbl_m, False, False, 0)

        btn = Gtk.Button()
        btn.add(box)
        btn.connect("clicked", lambda *_: self.insert_text(kan))
        btn.set_tooltip_text(
            f"{kan} / {yomi} / {meaning}"
        )

        return btn

    def refresh(self):
        for child in list(self.flow.get_children()):
            self.flow.remove(child)

        # quick & dirty: refresh
        self.items = load_kanjis()
        items = [it for it in self.items if self.matches(it)]
        for it in items:
            self.flow.add(self.make_tile(it))

        if not items:
            lbl = Gtk.Label(label="Brak wyników — zmień filtr.")
            lbl.set_xalign(0)
            self.flow.add(lbl)

        self.flow.show_all()

    def build_kana_keyboard(self) -> Gtk.Widget:
        wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # hiragana/katakana
        self.kana_mode = "hiragana"

        # Dakuten/Handakuten
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.mode_btn = Gtk.Button(label="Mode: Hiragana")
        self.mode_btn.connect("clicked", self.on_toggle_kana_mode)
        bar.pack_start(self.mode_btn, False, False, 0)

        dak = Gtk.Button(label="Dakuten (゛)")
        dak.connect("clicked", lambda *_: self.apply_last_kana_mark("dakuten"))
        bar.pack_start(dak, False, False, 0)

        han = Gtk.Button(label="Handakuten (゜)")
        han.connect("clicked", lambda *_: self.apply_last_kana_mark("handakuten"))
        bar.pack_start(han, False, False, 0)

        wrap.pack_start(bar, False, False, 0)

        # --- Basic kana grid ---
        rows = [
            ["あ", "い", "う", "え", "お"],
            ["か", "き", "く", "け", "こ"],
            ["さ", "し", "す", "せ", "そ"],
            ["た", "ち", "つ", "て", "と"],
            ["な", "に", "ぬ", "ね", "の"],
            ["は", "ひ", "ふ", "へ", "ほ"],
            ["ま", "み", "む", "め", "も"],
            ["や", "", "ゆ", "", "よ"],
            ["ら", "り", "る", "れ", "ろ"],
            ["わ", "", "", "", "を"],
            ["ん", "", "", "", ""],
        ]

        basic = Gtk.Grid(column_spacing=6, row_spacing=6)
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                btn = Gtk.Button()
                if ch:
                    btn.set_label(self.view_char(ch))
                    btn.connect(
                        "clicked", lambda _, x=ch: self.insert_text(self.view_char(x))
                    )
                else:
                    btn.set_sensitive(False)
                    btn.set_label(" ")
                    btn.set_opacity(0.0)
                basic.attach(btn, c, r, 1, 1)

        wrap.pack_start(Gtk.Label(label="Basic Kana"), False, False, 0)
        wrap.pack_start(basic, False, False, 0)

        # --- Small kana ---
        small_base = ["ゃ", "ゅ", "ょ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ", "っ"]
        small = Gtk.Grid(column_spacing=6, row_spacing=6)
        for i, ch in enumerate(small_base):
            btn = Gtk.Button(label=self.view_char(ch))
            btn.connect("clicked", lambda _, x=ch: self.insert_text(self.view_char(x)))
            small.attach(btn, i % 6, i // 6, 1, 1)

        wrap.pack_start(Gtk.Label(label="Small Kana"), False, False, 0)
        wrap.pack_start(small, False, False, 0)

        # --- Punctuation ---
        punct_list = [
            "。",
            "、",
            "・",
            "「",
            "」",
            "『",
            "』",
            "ー",
            "〜",
            "…",
            "？",
            "！",
        ]
        punct = Gtk.Grid(column_spacing=6, row_spacing=6)
        for i, ch in enumerate(punct_list):
            btn = Gtk.Button(label=self.view_char(ch))
            btn.connect("clicked", lambda _, x=ch: self.insert_text(self.view_char(x)))
            punct.attach(btn, i % 6, i // 6, 1, 1)

        wrap.pack_start(Gtk.Label(label="Punctuation"), False, False, 0)
        wrap.pack_start(punct, False, False, 0)

        # Keep buttons, pre-load labels
        self._kana_buttons = {
            "basic": basic,
            "small": small,
            "punct": punct,
        }

        return wrap

    def to_katakana(self, ch: str) -> str:
        cp = ord(ch)
        if 0x3041 <= cp <= 0x3096:
            return chr(cp + 0x60)
        return ch

    def to_hiragana(self, ch: str) -> str:
        cp = ord(ch)
        if 0x30A1 <= cp <= 0x30F6:
            return chr(cp - 0x60)
        return ch

    def view_char(self, ch: str) -> str:
        return self.to_katakana(ch) if self.kana_mode == "katakana" else ch

    def on_toggle_kana_mode(self, *_):
        self.kana_mode = "katakana" if self.kana_mode == "hiragana" else "hiragana"
        self.mode_btn.set_label(
            "Mode: Katakana" if self.kana_mode == "katakana" else "Mode: Hiragana"
        )
        self.rerender_kana_labels()

    def apply_last_kana_mark(self, kind: str):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end, True)
        if not txt:
            return

        arr = list(txt)  # Python string = codepoints; kana ok
        last = arr[-1]

        last_hira = self.to_hiragana(last)

        if kind == "dakuten":
            changed = DAKUTEN.get(last_hira)
        else:
            changed = HANDAKUTEN.get(last_hira)

        if not changed:
            return

        final = self.to_katakana(changed) if self.kana_mode == "katakana" else changed
        arr[-1] = final
        self.buf.set_text("".join(arr))

    def rerender_kana_labels(self):
        def update_grid(grid: Gtk.Grid):
            for child in grid.get_children():
                if isinstance(child, Gtk.Button):
                    label = child.get_label()
                    if not label or label.strip() == "":
                        continue
                    base = self.to_hiragana(label)
                    child.set_label(self.view_char(base))

        update_grid(self._kana_buttons["basic"])
        update_grid(self._kana_buttons["small"])
        update_grid(self._kana_buttons["punct"])


class KanjiApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        GLib.set_application_name("Kanji Catalogue")
        GLib.set_prgname("kanji-catalogue")
        win = KanjiPad(application=self)
        win.set_title("Kanji Catalogue")
        win.set_icon_from_file(str(ICON_PATH))
        win.show_all()
        win.present()
