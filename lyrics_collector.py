#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Morfonica 나무위키 가사 수집기 (ChromeDriver 버전)

설치:
    pip install undetected-chromedriver beautifulsoup4

실행:
    python lyrics_collector.py
"""

import csv
import re
import time
import urllib.parse
from pathlib import Path

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

BASE_DIR   = Path(__file__).parent
CACHE_PATH = BASE_DIR / "morfonica_lyrics_cache.txt"
CSV_PATH   = BASE_DIR / "morfonica.csv"
NAMU_BASE  = "https://namu.wiki/w/"

# \u escape 를 JS가 해석하도록 raw string + 실제 유니코드 문자 배제
EXTRACT_JS = (
    "(function() {"
    "  function isJapanese(t) { return /[\\u3041-\\u30FE\\u4E00-\\u9FFF]/.test(t); }"
    "  function hasKorean(t)  { return /[\\uAC00-\\uD7A3]/.test(t); }"
    "  var best = null, bestBr = 0;"
    "  document.querySelectorAll('td').forEach(function(td) {"
    "    var n = td.querySelectorAll('br').length;"
    "    var t = td.innerText;"
    "    if (n > 10 && isJapanese(t) && hasKorean(t) && n > bestBr) {"
    "      bestBr = n; best = td;"
    "    }"
    "  });"
    "  if (!best) return null;"
    "  var parts = best.innerHTML.split(/<br[^>]*>/i);"
    "  var lines = parts.map(function(p) { return p.replace(/<[^>]+>/g, '').trim(); });"
    "  var result = [];"
    "  var emptyCount = 0;"
    "  for (var i = 0; i < lines.length; i++) {"
    "    if (lines[i] === '') {"
    "      emptyCount++;"
    "    } else {"
    "      if (result.length > 0) {"
    "        if (emptyCount >= 2) { result.push(''); result.push(''); }"
    "        else if (emptyCount === 1) { result.push(''); }"
    "      }"
    "      emptyCount = 0;"
    "      result.push(lines[i]);"
    "    }"
    "  }"
    "  return result.join('\\n').trim();"
    "})()"
)


def load_cache() -> dict:
    cache = {}
    if not CACHE_PATH.exists():
        return cache
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


def append_cache(title: str, url: str, lyrics: str) -> None:
    with open(CACHE_PATH, "a", encoding="utf-8") as f:
        f.write(f"제목: {title}\nURL: {url}\n가사:\n{lyrics}\n<<<END>>>\n")


def main() -> None:
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    if "번역가사 링크" not in fieldnames:
        fieldnames.append("번역가사 링크")
        for row in rows:
            row.setdefault("번역가사 링크", "")

    cache = load_cache()
    print(f"캐시 로드: {len(cache)}곡 이미 수집됨")

    needs_fetch = []
    for row in rows:
        title = row.get("제목(원어)", "").strip()
        if not title:
            continue
        if title in cache:
            row["번역가사 링크"] = cache[title]["url"]
        else:
            needs_fetch.append(row)

    if not needs_fetch:
        print("모든 곡이 캐시에 있습니다.")
    else:
        options = uc.ChromeOptions()
        options.add_argument("--lang=ko-KR")
        options.add_argument("--window-size=1280,800")
        driver = uc.Chrome(options=options, version_main=148)
        success, fail = [], []

        try:
            for row in needs_fetch:
                title = row.get("제목(원어)", "").strip()
                # 원제목으로 먼저 시도하고, 가사를 못 찾으면
                # "(BanG Dream!)" 동음이의 문서명을 붙여 재시도
                candidates = [title, f"{title}(BanG Dream!)"]
                print(f"[GET ] {title}")
                try:
                    lyrics = None
                    url = ""
                    for cand in candidates:
                        url = NAMU_BASE + urllib.parse.quote(cand)
                        print(f"       {url}")
                        driver.get(url)
                        time.sleep(3)
                        lyrics = driver.execute_script(EXTRACT_JS)
                        if not lyrics:
                            lyrics = _bs4_fallback(driver.page_source)
                        if lyrics:
                            break
                        print(f"       ↳ 미탐지, 다음 후보 시도")
                    if lyrics:
                        lyrics = lyrics.strip()
                        append_cache(title, url, lyrics)
                        row["번역가사 링크"] = url
                        print(f"       OK ({len(lyrics)}자)")
                        success.append(title)
                    else:
                        print(f"       ✗ 가사 없음")
                        fail.append(title)
                except Exception as e:
                    print(f"       Error: {e}")
                    fail.append(title)
                time.sleep(2)
        finally:
            driver.quit()

        print(f"\n완료: {len(success)}곡 저장, {len(fail)}곡 실패")
        if fail:
            print(f"실패: {', '.join(fail)}")

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("CSV 업데이트 완료")


def _bs4_fallback(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    best_td, best_br = None, 0
    for td in soup.find_all("td"):
        br_count = len(td.find_all("br"))
        text = td.get_text()
        if br_count > 10 and _is_japanese(text) and _is_korean(text) and br_count > best_br:
            best_br = br_count
            best_td = td
    if not best_td:
        return None
    parts = re.split(r"<br[^>]*>", str(best_td))
    lines = [re.sub(r"<[^>]+>", "", p).strip() for p in parts]
    result, empty_count = [], 0
    for line in lines:
        if line == "":
            empty_count += 1
        else:
            if result:
                if empty_count >= 2:
                    result += ["", ""]
                elif empty_count == 1:
                    result.append("")
            empty_count = 0
            result.append(line)
    return "\n".join(result).strip()


def _is_japanese(text: str) -> bool:
    return any(0x3041 <= ord(c) <= 0x30FE or 0x4E00 <= ord(c) <= 0x9FFF for c in text)


def _is_korean(text: str) -> bool:
    return any(0xAC00 <= ord(c) <= 0xD7A3 for c in text)


if __name__ == "__main__":
    main()
