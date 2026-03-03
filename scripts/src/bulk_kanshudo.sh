#!/usr/bin/env bash
set -euo pipefail

KANJI='日一二一二三四五十人大小中上下前後年月時間今本見行生出死話思世界春夏秋冬何帰先輩風吹張栄来言好猫食聞銀神髪紙責電書類分取多自気天元少金水買歩飛持飲犬花手火曜赤若達違通暑入昔練習待近去邪毎色黄室使読屋部音楽嘘'

for (( i=0; i<${#KANJI}; i++ )); do
  k="${KANJI:i:1}"
  echo ">>> $k"
  kanshudo "$k" --save
  sleep 1
done
