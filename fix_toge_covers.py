#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
toge.csv 의 앨범커버를 iTunes(Apple Music) 공식 아트워크로 교체.
- 기존 i.namu.wiki 링크는 Cloudflare 핫링크 차단(403)으로 깃헙io에서 깨짐
- mzstatic.com 은 핫링크 허용 → 안정적
사용:  python fix_toge_covers.py --dry   # 매칭 미리보기
       python fix_toge_covers.py         # 실제 교체
"""
import csv, sys, json, time, urllib.parse, urllib.request, re, unicodedata
from pathlib import Path

CSV = Path(__file__).parent / "toge.csv"
DRY = "--dry" in sys.argv
ART = "トゲナシトゲアリ"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).replace("​", "")
    return re.sub(r"\s+", "", s).lower().strip()


def itunes(title: str):
    term = urllib.parse.quote(f"{title} {ART}")
    url = f"https://itunes.apple.com/search?term={term}&country=jp&entity=song&limit=15"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req, timeout=20))
    return data.get("results", [])


def pick(title: str, results: list):
    nt = norm(title)
    exact = [r for r in results if norm(r.get("trackName", "")) == nt]
    toge = [r for r in exact if ART in r.get("artistName", "")]
    chosen = (toge or exact or results)
    return chosen[0] if chosen else None


def art_url(r: dict) -> str:
    # 100x100 → 600x600 업스케일
    return r["artworkUrl100"].replace("100x100bb.jpg", "600x600bb.jpg")


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    fieldnames = list(rows[0].keys())
    hit = miss = 0
    for r in rows:
        title = r["제목(원어)"].strip()
        try:
            results = itunes(title)
            m = pick(title, results)
        except Exception as e:
            m = None
            print(f"  ERROR {title}: {e}")
        time.sleep(0.4)
        if m:
            hit += 1
            url = art_url(m)
            flag = "" if ART in m.get("artistName", "") else "  <-- 아티스트확인"
            print(f"OK  {title}  ->  {m['trackName']} / {m['artistName']}{flag}")
            r["_new"] = url
        else:
            miss += 1
            print(f"MISS {title}  (검색 결과 없음)")
            r["_new"] = ""

    print(f"\n매칭: {hit} 성공 / {miss} 실패")

    if DRY:
        return
    for r in rows:
        if r.get("_new"):
            r["앨범커버"] = r["_new"]
        r.pop("_new", None)
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)
    print("toge.csv 업데이트 완료")


if __name__ == "__main__":
    main()
