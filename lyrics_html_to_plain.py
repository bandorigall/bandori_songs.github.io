#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lyrics/*.txt 중 HTML 구조(<p>, <span style> 등)로 저장된 가사 파일을
모르포니카처럼 순수 텍스트(원어/발음/번역 + 그룹 사이 빈 줄)로 변환.

- 변환 전 원본을 lyrics_html_backup/ 에 백업
- <p> 한 개 = 한 줄,  빈 <p>(또는 <br>만 있는 줄) = 그룹 구분 빈 줄
- 그룹 내부는 줄바꿈 1개, 그룹 사이는 빈 줄 1개 → convert_html.format_lyrics 의 i%3 색 분리와 호환

사용:  python lyrics_html_to_plain.py            # 변환 실행
       python lyrics_html_to_plain.py --dry      # 미리보기만
"""
import sys
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path(__file__).parent
LYRICS = BASE / "lyrics"
BACKUP = BASE / "lyrics_html_backup"

DRY = "--dry" in sys.argv

HTML_MARKERS = ("<p", "<span", "<br", "<font", "<div")


def is_html(text: str) -> bool:
    return any(m in text for m in HTML_MARKERS)


def html_to_plain(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    # p/div 같은 블록 요소를 한 줄로 취급 (중첩 블록은 제외하고 leaf만)
    blocks = [b for b in soup.find_all(["p", "div"]) if not b.find(["p", "div"])]
    if blocks:
        text = "\n".join(b.get_text() for b in blocks)
    else:
        text = soup.get_text()

    # 줄 단위 정리 + 연속 빈 줄을 1개로 축소
    lines = [ln.strip() for ln in text.split("\n")]
    out = []
    for ln in lines:
        if ln == "" and (not out or out[-1] == ""):
            continue
        out.append(ln)
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def main() -> None:
    if not DRY:
        BACKUP.mkdir(exist_ok=True)

    converted = skipped = 0
    for txt in sorted(LYRICS.glob("*.txt")):
        raw = txt.read_text(encoding="utf-8")
        if not is_html(raw):
            skipped += 1
            continue

        plain = html_to_plain(raw)
        converted += 1

        if DRY:
            print(f"\n===== {txt.name} =====")
            print(plain[:300])
            continue

        shutil.copy2(txt, BACKUP / txt.name)
        txt.write_text(plain, encoding="utf-8")
        print(f"변환: {txt.name}")

    print(f"\n완료: {converted}곡 변환, {skipped}곡 순수텍스트(건너뜀)")
    if not DRY:
        print(f"원본 백업: {BACKUP}")


if __name__ == "__main__":
    main()
