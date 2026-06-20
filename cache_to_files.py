#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
morfonica_lyrics_cache.txt 를 파싱해서
  - lyrics/제목(원어).txt 저장
  - morfonica.csv 번역가사 링크 업데이트
"""

import csv
import sys
from pathlib import Path

# 밴드명을 인자로 받음 (없으면 morfonica). 예: python cache_to_files.py afterglow
BAND = sys.argv[1] if len(sys.argv) > 1 else "morfonica"

BASE_DIR   = Path(__file__).parent
CACHE_PATH = BASE_DIR / f"{BAND}_lyrics_cache.txt"
LYRICS_DIR = BASE_DIR / "lyrics"
CSV_PATH   = BASE_DIR / f"{BAND}.csv"


def load_cache() -> dict[str, dict]:
    cache = {}
    entries = CACHE_PATH.read_text(encoding="utf-8").split("\n<<<END>>>\n")
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        lines = entry.splitlines()
        title = url = ""
        lyrics_lines = []
        in_lyrics = False
        for line in lines:
            if line.startswith("제목: "):
                title = line[4:].strip()
            elif line.startswith("URL: "):
                url = line[5:].strip()
            elif line == "가사:":
                in_lyrics = True
            elif in_lyrics:
                lyrics_lines.append(line)
        if title:
            cache[title] = {"url": url, "lyrics": "\n".join(lyrics_lines).strip()}
    return cache


def main() -> None:
    LYRICS_DIR.mkdir(exist_ok=True)
    cache = load_cache()
    print(f"캐시에서 {len(cache)}곡 로드")

    # 1. lyrics/*.txt 저장
    #    Windows 금지문자(\ / : * ? " < > |) 제거 — convert_html은 제목 정규화로
    #    매칭하므로 파일명에서 이 문자들을 빼도 매칭에 영향 없음
    import re as _re
    for title, data in cache.items():
        safe = _re.sub(r'[\\/:*?"<>|]', '', title).strip()
        txt_path = LYRICS_DIR / f"{safe}.txt"
        txt_path.write_text(data["lyrics"], encoding="utf-8")
        print(f"  저장: {txt_path.name}")

    # 2. CSV 번역가사 링크 업데이트
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    updated = 0
    for row in rows:
        title = row.get("제목(원어)", "").strip()
        if title in cache:
            row["번역가사 링크"] = cache[title]["url"]
            updated += 1

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n완료: .txt {len(cache)}개 저장, CSV {updated}곡 링크 업데이트")


if __name__ == "__main__":
    main()
