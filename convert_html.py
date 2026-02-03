import pandas as pd
from bs4 import BeautifulSoup
import os
import html
from datetime import datetime

# ---------------------------------------------------------
# 설정
# ---------------------------------------------------------
LYRICS_FOLDER = "lyrics"
OUTPUT_FILENAME = "index.html"
TODAY_DATE = datetime.now().strftime("%Y.%m.%d")

# 밴드별 설정
csv_files = {
    "mygo.csv": {
        "name": "MyGO!!!!!",
        "color": "#4682B4", 
        "bg_color": "rgba(70, 130, 180, 0.05)",
        "logo": "mygo.webp"
    },
    "ave.csv": {
        "name": "Ave Mujica",
        "color": "#8A2BE2", 
        "bg_color": "rgba(138, 43, 226, 0.05)",
        "logo": "ave.webp"
    },
    "afterglow.csv": {
        "name": "Afterglow",
        "color": "#ee3344", 
        "bg_color": "rgba(238, 51, 68, 0.05)",
        "logo": "afterglow.webp"
    },
    "yumemita.csv": {
        "name": "夢限大みゅーたいぷ",
        "color": "#FF69B4", 
        "bg_color": "rgba(255, 105, 180, 0.05)",
        "logo": "yumemita.webp"
    },
}

# ---------------------------------------------------------
# HTML 템플릿 (CSS 수정됨)
# ---------------------------------------------------------
html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>뱅드림 발매곡 목록</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-bg: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #2d3436;
            --border-color: #eee;
        }}
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            background-color: var(--primary-bg);
            color: var(--text-color);
            margin: 0;
            padding: 40px 20px 20px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            width: 100%;
            max-width: 1000px;
            background: var(--card-bg);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.08);
            overflow: hidden;
            margin-bottom: 30px;
        }}
        .nav-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fff;
            border-bottom: 1px solid #f1f1f1;
            padding: 12px 25px;
        }}
        .last-update {{
            font-size: 11px;
            color: #aaa;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .tab-group {{ display: flex; overflow-x: auto; }}
        .tab-button {{
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid transparent;
            background: none;
            cursor: pointer;
            transition: all 0.2s ease;
            color: #888;
            border-radius: 20px;
            margin-left: 6px;
            white-space: nowrap;
        }}
        .tab-button:hover {{ background-color: #f0f0f0; color: #333; }}
        .tab-button.active {{
            background-color: #333;
            color: #fff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .band-logo-area {{ text-align: center; padding: 30px 0 10px 0; }}
        .band-logo-area img {{
            max-height: 120px; max-width: 80%;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }}
        .content {{ display: none; padding-bottom: 40px; }}
        .content.active {{ display: block; animation: fadeIn 0.4s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .table-wrapper {{ overflow-x: auto; padding: 0 20px; }}
        table {{ width: 100%; border-collapse: separate; border-spacing: 0 8px; }}
        th {{
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            border-bottom: 2px solid #eee;
        }}
        td {{
            padding: 12px 16px;
            vertical-align: middle;
            background: #fff;
            border-top: 1px solid #f9f9f9;
            border-bottom: 1px solid #f9f9f9;
        }}
        td:first-child {{ border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-left: 1px solid #f9f9f9; }}
        td:last-child {{ border-top-right-radius: 10px; border-bottom-right-radius: 10px; border-right: 1px solid #f9f9f9; }}
        
        /* 곡 정보 클릭 영역 스타일 개선 */
        .song-info-wrapper {{ 
            display: flex; 
            align-items: center; 
            min-width: 200px;
            padding: 5px;
            border-radius: 8px;
            transition: background-color 0.2s;
        }}
        /* 가사가 있는 경우 클릭 가능 표시 */
        .clickable-song {{
            cursor: pointer;
        }}
        .clickable-song:hover {{
            background-color: #f1f3f5;
        }}
        .clickable-song:active {{
            background-color: #e9ecef;
            transform: scale(0.99);
        }}

        .album-thumb {{
            width: 52px; height: 52px;
            border-radius: 8px;
            object-fit: cover;
            margin-right: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex-shrink: 0;
            background-color: #eee;
        }}
        .song-text {{ display: flex; flex-direction: column; }}
        .song-title-main {{ font-size: 1.05em; font-weight: 700; color: #333; margin-bottom: 2px; }}
        .song-title-sub {{ font-size: 0.8em; color: #999; }}
        
        .meta-info {{ display: flex; flex-direction: column; gap: 4px; font-size: 12px; min-width: 100px; }}
        .meta-top {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .release-date {{ color: #888; font-family: monospace; letter-spacing: -0.5px; }}
        .meta-desc {{ color: #666; font-size: 11px; }}
        .badge {{ padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block; }}
        .badge-original {{ background-color: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }}
        .badge-cover {{ background-color: #fff3e0; color: #f57c00; border: 1px solid #ffe0b2; }}
        .badge-tieup {{ background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }}
        
        .btn {{
            display: inline-flex; align-items: center; justify-content: center;
            text-decoration: none; font-weight: 600; padding: 6px 12px;
            border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; border: none; white-space: nowrap;
        }}
        .btn-link {{ background-color: #f1f3f5; color: #495057; }}
        .btn-link:hover {{ background-color: #e9ecef; color: #212529; }}
        
        .source-container {{ margin-top: 30px; padding-top: 15px; border-top: 1px dashed #eee; text-align: center; }}
        .source-link-btn {{
            display: inline-block; padding: 5px 12px; background-color: #f1f3f5;
            color: #868e96; text-decoration: none; border-radius: 15px; font-size: 11px; font-weight: 500; transition: all 0.2s;
        }}
        .source-link-btn:hover {{ background-color: #e9ecef; color: #495057; }}
        .footer {{ margin-top: auto; font-size: 11px; color: #ccc; text-align: center; padding-bottom: 10px; }}
        
        /* 모달 창 */
        .modal-overlay {{
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(5px); z-index: 1000;
        }}
        .modal-box {{
            position: relative; background: #fff; width: 90%; max-width: 500px;
            margin: 8% auto; border-radius: 20px; max-height: 80vh;
            display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .modal-header {{ padding: 20px 25px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }}
        .modal-body {{ padding: 30px; overflow-y: auto; line-height: 1.8; white-space: pre-wrap; font-size: 16px; text-align: center; color: #444; }}
        .close-btn {{ font-size: 28px; cursor: pointer; border: none; background: none; color: #ccc; }}
        .close-btn:hover {{ color: #333; }}
        
        /* 모바일 대응: 표 헤더 숨김 등 */
        @media (max-width: 600px) {{
            th {{ display: none; }} /* 헤더 숨김으로 공간 절약 */
            .song-info-wrapper {{ min-width: auto; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="nav-header">
        <div class="last-update">Last Update: {today_date}</div>
        <div class="tab-group" id="tab-nav">{tab_buttons}</div>
    </div>
    {table_contents}
</div>
<div class="footer">made by Bangbung Kim</div>
<div id="lyrics-modal" class="modal-overlay" onclick="closeModal()">
    <div class="modal-box" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3 id="modal-title" style="margin:0; font-size:1.2em;"></h3>
            <button class="close-btn" onclick="closeModal()">&times;</button>
        </div>
        <div id="modal-body" class="modal-body"></div>
    </div>
</div>
<script>
    function openTab(evt, tabName) {{
        var i, content, tablinks;
        content = document.getElementsByClassName("content");
        for (i = 0; i < content.length; i++) content[i].classList.remove("active");
        tablinks = document.getElementsByClassName("tab-button");
        for (i = 0; i < tablinks.length; i++) tablinks[i].classList.remove("active");
        document.getElementById(tabName).classList.add("active");
        evt.currentTarget.classList.add("active");
    }}
    function showLyrics(uniqueId, title) {{
        var scriptEl = document.getElementById('lyrics-' + uniqueId);
        if (!scriptEl) return;
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-body').innerHTML = scriptEl.innerHTML;
        document.getElementById('lyrics-modal').style.display = 'block';
        document.body.style.overflow = 'hidden';
    }}
    function closeModal() {{
        document.getElementById('lyrics-modal').style.display = 'none';
        document.body.style.overflow = 'auto';
    }}
    document.addEventListener('keydown', function(event) {{ if (event.key === "Escape") closeModal(); }});
    document.addEventListener("DOMContentLoaded", function() {{
        var firstTab = document.querySelector(".tab-button");
        if(firstTab) firstTab.click();
    }});
</script>
</body>
</html>
"""

tabs_html = ""
tables_html = ""
title_counts = {}

for index, (file, info) in enumerate(csv_files.items()):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"파일 없음: {file}")
        continue

    # 1. 상세정보 통합 (타이업도 원곡가수 표시)
    def merge_meta_info(row):
        release_date = str(row.get('발매일 / 커버일', '-')).strip()
        song_type = str(row.get('곡유형', '')).strip()
        orig_artist = str(row.get('원곡가수', '')).strip()
        badge_html = ""
        desc_text = ""
        if "오리지널" in song_type:
            badge_html = '<span class="badge badge-original">ORIGINAL</span>'
        elif "타이업" in song_type:
            badge_html = '<span class="badge badge-tieup">TIE-UP</span>'
            if orig_artist and orig_artist != "nan":
                desc_text = f"Original by {orig_artist}"
        elif "커버" in song_type:
            badge_html = '<span class="badge badge-cover">COVER</span>'
            if orig_artist and orig_artist != "nan":
                desc_text = f"Original by {orig_artist}"
        meta_html = f'<div class="meta-info"><div class="meta-top">{badge_html}<span class="release-date">{release_date}</span></div>'
        if desc_text:
            meta_html += f'<span class="meta-desc">{desc_text}</span>'
        meta_html += '</div>'
        return meta_html

    df["상세정보"] = df.apply(merge_meta_info, axis=1)

    # 2. 링크 처리
    def create_link_btn(url):
        if pd.isna(url) or not str(url).strip().startswith("http"): return ""
        return f'<a href="{url}" target="_blank" class="btn btn-link">Listen</a>'

    if "링크" in df.columns:
        df["링크"] = df["링크"].apply(create_link_btn)

    # 3. 곡명 + 가사 통합 처리 (핵심 변경 부분)
    # 기존 apply 대신 iterrows로 직접 HTML을 생성합니다.
    song_column_data = []
    
    for idx, row in df.iterrows():
        # 기본 정보 추출
        title_jp = str(row.get('제목(원어)', '')).strip()
        title_kr = str(row.get('제목(한국어)', '')).strip()
        cover_url = row.get('앨범커버')
        ext_link = row.get('번역가사 링크')

        # 가사 파일 확인 로직
        title_counts[title_jp] = title_counts.get(title_jp, 0) + 1
        suffix = f"_{title_counts[title_jp]}" if title_counts[title_jp] > 1 else ""
        filename = f"{title_jp}{suffix}.txt"
        filepath = os.path.join(LYRICS_FOLDER, filename)
        unique_id = f"{index}_{idx}"
        
        script_html = ""
        onclick_attr = ""
        wrapper_class = "song-info-wrapper"
        
        # 가사가 있는 경우
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().replace('\\r', '').replace('\\n', '<br>').replace('\r\n', '<br>').replace('\n', '<br>')
            if pd.notna(ext_link) and str(ext_link).strip().startswith("http"):
                source_btn_html = f'<div class="source-container"><a href="{ext_link}" target="_blank" class="source-link-btn">출처</a></div>'
                content += source_btn_html
            
            safe_title = html.escape(title_jp)
            # 가사 내용을 담은 숨겨진 script 태그 생성
            script_html = f'<script id="lyrics-{unique_id}" type="text/template">{content}</script>'
            # 클릭 이벤트 추가
            onclick_attr = f'onclick="showLyrics(\'{unique_id}\', \'{safe_title}\')"'
            wrapper_class += " clickable-song"

        # 곡 정보 HTML 생성 (클릭 이벤트 포함)
        text_html = f'<div class="song-text"><span class="song-title-main">{title_jp}</span>'
        if title_kr and title_kr != "nan":
            text_html += f'<span class="song-title-sub">{title_kr}</span>'
        text_html += '</div>'
        
        if pd.notna(cover_url) and isinstance(cover_url, str) and cover_url.strip() != "":
            # 앨범 커버 클릭시 새탭 열기 방지를 위해 img 태그만 사용하거나, 
            # 전체 클릭과 충돌을 막기 위해 event.stopPropagation()을 넣을 수 있으나
            # 여기서는 전체 클릭이 우선되도록 a태그를 제거하고 이미지만 넣습니다.
            # (만약 커버 클릭시 확대 기능을 원하시면 별도 처리가 필요합니다)
            img_html = f'<img src="{cover_url}" class="album-thumb" alt="cover">'
        else:
            img_html = '<div class="album-thumb" style="background:#f0f0f0;"></div>'
            
        final_cell_html = f'<div class="{wrapper_class}" {onclick_attr}>{img_html}{text_html}</div>{script_html}'
        song_column_data.append(final_cell_html)

    df["곡명"] = song_column_data

    # 최종 컬럼 선택 (가사 컬럼 제거)
    final_df = df[["곡명", "상세정보", "링크"]]
    table_html = final_df.to_html(index=False, escape=False, border=0)
    
    tab_id = f"tab-{index}"
    tabs_html += f'<button class="tab-button" onclick="openTab(event, \'{tab_id}\')">{info["name"]}</button>'
    logo_html = f'<img src="{info.get("logo", "")}" alt="{info["name"]}">' if info.get("logo") else f'<h1>{info["name"]}</h1>'
    tables_html += f'<div id="{tab_id}" class="content"><div class="band-logo-area">{logo_html}</div><div class="table-wrapper">{table_html}</div></div>'

final_output = html_template.format(today_date=TODAY_DATE, tab_buttons=tabs_html, table_contents=tables_html)

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
    f.write(final_output)

print(f"\n🎉 {OUTPUT_FILENAME} 생성 완료! (모바일 최적화: 곡명 클릭 시 가사 팝업)")