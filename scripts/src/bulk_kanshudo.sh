#!/usr/bin/env bash
#
# NOTE: this is not importer per-se. It uses very slow mechanism and it's here
# just for testing. Import may take a while!
#
set -euo pipefail

KANJI="$(python ./src/top_kanjis.py)"

for (( i=0; i<${#KANJI}; i++ )); do
  k="${KANJI:i:1}"
  echo ">>> $k"
  kanji "$k" --save
  sleep 1
done
