#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
morfonica.csv 의 링크 컬럼을 공식 재생목록 기준으로 교체
https://www.youtube.com/playlist?list=PLkc6qZ_s5R1vIj_3GNgmIwf0teEEdCe6K
"""

import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent / "morfonica.csv"

# 재생목록에서 추출한 제목(원어) → 유튜브 URL 매핑
PLAYLIST_MAP = {
    "Daylight -デイライト-":     "https://www.youtube.com/watch?v=DhYniTbW2P0",
    "金色へのプレリュード":         "https://www.youtube.com/watch?v=Qam2U-LF_Ks",
    "ブルームブルーム":             "https://www.youtube.com/watch?v=ulnZ8yiS7Jg",
    "flame of hope":              "https://www.youtube.com/watch?v=4kLyLp8Oco0",
    "ハーモニー・デイ":             "https://www.youtube.com/watch?v=NuhjVeWwvoM",
    "Sonorous":                   "https://www.youtube.com/watch?v=Wl5LZ3iJNzM",
    "Fateful...":                 "https://www.youtube.com/watch?v=RD_6TSNkxg0",
    "fly with the night":         "https://www.youtube.com/watch?v=DpnFf8UINbs",
    "Secret Dawn":                "https://www.youtube.com/watch?v=eWqv5RB6jng",
    "寄る辺のSunny, Sunny":        "https://www.youtube.com/watch?v=6C4NOz-t3QA",
    "One step at a time":         "https://www.youtube.com/watch?v=T_a1YLnxD50",
    "The Circle Of Butterflies":  "https://www.youtube.com/watch?v=6jbetrvXxBI",
    "メランコリックララバイ":         "https://www.youtube.com/watch?v=D_uUbtZUOPc",
    "カラフルリバティー":            "https://www.youtube.com/watch?v=HqDa4NOAt8w",
    "Sweet Cheers!":              "https://www.youtube.com/watch?v=e8IQBZMVIGw",
    "誓いのWingbeat":              "https://www.youtube.com/watch?v=nnpD32__lAY",
    "Ever Sky Blue":              "https://www.youtube.com/watch?v=Ar7QtswUNGw",
    "Angel's Ladder":             "https://www.youtube.com/watch?v=QzMSltHeHTw",
    "フレージング ミラージュ":        "https://www.youtube.com/watch?v=yuG78deMpUo",
    "MUGEN Reverberate!":         "https://www.youtube.com/watch?v=B6602-OMtZI",
    "わたしまちがいさがし":           "https://www.youtube.com/watch?v=mKGMgDGj0kQ",
    "esora no clover":            "https://www.youtube.com/watch?v=fGgKN9_egCM",
    "きょうもMerry go rounD":       "https://www.youtube.com/watch?v=j4n8YgcCTFE",
    "両翼のBrilliance":            "https://www.youtube.com/watch?v=4AoDp2E5mJk",
    "音がえしのセレナーデ":           "https://www.youtube.com/watch?v=sUaDAY9u4y8",
    "蒼穹へのトレイル":              "https://www.youtube.com/watch?v=eAjX1Ihvtac",
    "Tempest":                    "https://www.youtube.com/watch?v=3TR0asiF9ik",
    "Wreath of Brave":            "https://www.youtube.com/watch?v=5O3gAE65_34",
    "Polyphonyscape":             "https://www.youtube.com/watch?v=inV8PDIgZDo",
    "Merry Merry Thanks!!":       "https://www.youtube.com/watch?v=j3W3NHurJnk",
    "Steer to Utopia":            "https://www.youtube.com/watch?v=wjpVRH7GOFc",
    "ティリカモニカリラ":             "https://www.youtube.com/watch?v=d32zOmV118k",
    "Feathered Dreams":           "https://www.youtube.com/watch?v=sAnwgtsAzs8",
    "Color of Us":                "https://www.youtube.com/watch?v=x9I1W3Aigrc",
    "Portray Empathy":            "https://www.youtube.com/watch?v=A-8Ci-YRgjE",
    "ビューティ・フォー":             "https://www.youtube.com/watch?v=PtLt1G-Xcyg",
    "Resonant Strings":           "https://www.youtube.com/watch?v=cKAlPDZX-PY",
    "Shining Leaves":             "https://www.youtube.com/watch?v=HkruyxEhOPI",
    "胡蝶翔る星月夜":               "https://www.youtube.com/watch?v=GOU_X0KK-jo",
}

with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

updated = 0
not_found = []
for row in rows:
    title = row.get("제목(원어)", "").strip()
    if title in PLAYLIST_MAP:
        old = row.get("링크", "")
        row["링크"] = PLAYLIST_MAP[title]
        if old != row["링크"]:
            print(f"  변경: {title}")
            print(f"    전: {old}")
            print(f"    후: {row['링크']}")
        updated += 1
    elif title:
        not_found.append(title)

with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n완료: {updated}곡 업데이트")
if not_found:
    print(f"재생목록에 없음: {not_found}")
