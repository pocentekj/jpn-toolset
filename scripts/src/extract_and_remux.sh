#!/usr/bin/env bash
set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }

# --- input ---
if [[ $# -ge 1 ]]; then
  in="$1"
else
  mapfile -t mkvs < <(find . -maxdepth 1 -type f -name '*.mkv' -printf '%P\n' | sort)
  [[ ${#mkvs[@]} -eq 1 ]] || die "Expected exactly 1 *.mkv in current dir (found ${#mkvs[@]}). Pass a filename as argument."
  in="${mkvs[0]}"
fi

[[ -f "$in" ]] || die "File not found: $in"

base="${in%.mkv}"
ass="${base}.ass"
srt="${base}.srt"
tmp="${base}.tmp.mkv"

command -v ffmpeg >/dev/null 2>&1 || die "ffmpeg not found in PATH"
command -v ffprobe >/dev/null 2>&1 || die "ffprobe not found in PATH"
command -v subtitleedit >/dev/null 2>&1 || die "subtitleedit not found in PATH"

# --- 1) extract JP ASS (stream 0:5) ---
ffmpeg -hide_banner -y \
  -i "$in" \
  -map 0:5 -c copy \
  "$ass"

# --- 2) remux MKV without JP subs; set defaults (audio jpn, subs eng full) ---
ffmpeg -hide_banner -y \
  -i "$in" \
  -map 0 -map -0:5 \
  -c copy \
  -disposition:0 0 \
  -disposition:1 0 \
  -disposition:2 0 \
  -disposition:3 0 \
  -disposition:4 0 \
  -disposition:2 default \
  -disposition:4 default \
  "$tmp"

mv -f -- "$tmp" "$in"

# --- 3) convert ASS -> clean SRT (strip formatting) ---
subtitleedit \
  /convert "$ass" srt \
  /outputfilename:"$srt" \
  /RemoveFormatting \
  /overwrite

echo "OK:"
echo "  MKV updated: $in"
echo "  ASS extracted: $ass"
echo "  SRT created: $srt"
