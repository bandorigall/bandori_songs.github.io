#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCinside(gall.dcinside.com) 가사 게시글 본문에서 가사를 추출해
lyrics/제목(원어).txt 로 저장. ave.csv 의 '번역가사 링크'(DC) 기준.

- 본문 .write_div 에서 원어/발음/번역 3줄 그룹만 추출
- 맨 앞 크레딧(작사/작곡/일러스트/MV/Twitter)·잡담 블록 제거
- 이미 lyrics/ 에 있는 곡은 스킵

사용:  python dc_lyrics_collector.py --dry [제목]   # 미리보기
       python dc_lyrics_collector.py                # 실제 저장
"""
import csv, sys, os, re, time, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path(__file__).parent
CSV = BASE / "ave.csv"
LYRICS = BASE / "lyrics"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

DRY = "--dry" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

CREDIT = re.compile(r"(작사|작곡|편곡|일러스트|illust|MV|Twitter|@|참고|보컬|영상|제작|믹싱|마스터)", re.I)


def has_hangul(s):
    return any("가" <= c <= "힣" for c in s)


def safe_filename(title):
    # Windows 금지문자 제거 (convert_html 매칭은 특수문자 무시라 영향 없음)
    return re.sub(r'[<>:"/\\|?*]', "", title).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    wd = soup.select_one(".write_div")
    if not wd:
        return None
    # 인라인 태그 unwrap → 한 줄이 여러 span 으로 쪼개지는 것 방지
    for tag in wd.find_all(["span", "font", "b", "i", "strong", "em", "u", "a", "small"]):
        tag.unwrap()
    for br in wd.find_all("br"):
        br.replace_with("\n")
    return wd.get_text("\n")


def extract_lyrics(body):
    # 빈 줄 개수에 의존하지 않도록: 비어있지 않은 줄만 사용
    seq = [l.strip() for l in body.split("\n") if l.strip()]

    # 가사 시작 = (크레딧 아님) & (원어=비한글) & (다음 줄이 한글=발음)
    start = None
    for k in range(len(seq) - 1):
        if has_hangul(seq[k]) or CREDIT.search(seq[k]):
            continue
        if has_hangul(seq[k + 1]):
            start = k
            break
    if start is None:
        return ""

    # 시작 이후, 크레딧/잡담(footer 등) 줄 제거
    lyr = [l for l in seq[start:] if not CREDIT.search(l)]

    # 원어(비한글) + 뒤따르는 한글들 = 한 그룹, 그룹 사이 빈 줄
    groups, cur, prev_h = [], [], False
    for l in lyr:
        h = has_hangul(l)
        if not h and prev_h and cur:      # 한글 → 원어 전환점에서 새 그룹
            groups.append(cur)
            cur = []
        cur.append(l)
        prev_h = h
    if cur:
        groups.append(cur)

    return "\n\n".join("\n".join(g) for g in groups).strip()


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    done = ok = skip = fail = 0
    for r in rows:
        title = r["제목(원어)"].strip()
        link = r.get("번역가사 링크", "").strip()
        if ONLY and title not in ONLY:
            continue
        out = LYRICS / f"{safe_filename(title)}.txt"
        if out.exists() and not ONLY:
            skip += 1
            continue
        if "dcinside" not in link:
            continue
        try:
            body = fetch(link)
            lyrics = extract_lyrics(body) if body else ""
        except Exception as e:
            print(f"  ERROR {title}: {e}")
            fail += 1
            continue
        time.sleep(1.0)
        if not lyrics or len(lyrics) < 40:
            print(f"  ✗ 추출 실패/빈약 | {title}")
            fail += 1
            continue
        ok += 1
        if DRY:
            print(f"\n===== {title} ({len(lyrics)}자) =====")
            print(lyrics[:400])
        else:
            out.write_text(lyrics, encoding="utf-8")
            print(f"저장: {title}.txt ({len(lyrics)}자)")
    print(f"\n완료: {ok} 추출, {skip} 스킵(이미있음), {fail} 실패")


if __name__ == "__main__":
    main()
