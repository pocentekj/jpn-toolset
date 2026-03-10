# Katakana to hiragana converter

I use it to quickly convert katakana characters to hiragana in input stream.

As I've found katakana characters hard to read sometimes (especially single characters or unusual fonts) I'm using this simple tool to convert them to hiragana, like this:

```bash
echo "ャュョァィゥェォッ"|kata-to-hira --color
```

Repository contains only source code (which is very simple indeed 😅) so you need Rust toolchain to build it. There are no dependencies.
