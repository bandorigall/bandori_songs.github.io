import pandas as pd
import os
import html
import re
import unicodedata
from datetime import datetime

# ---------------------------------------------------------
# 설정
# ---------------------------------------------------------
LYRICS_FOLDER = "lyrics"
OUTPUT_FILENAME = "index.html"
TODAY_DATE = datetime.now().strftime("%Y.%m.%d")

# 밴드별 설정
csv_files = {
    "poppin_party.csv": {
        "name": "Poppin'Party",
        "color": "#FF55BB",
        "logo": "poppin_party.png"
    },
    "afterglow.csv": {
        "name": "Afterglow",
        "color": "#EE3344",
        "logo": "afterglow.webp"
    },
    "pastel_palettes.csv": {
        "name": "Pastel＊Palettes",
        "color": "#77FFCC",
        "logo": "pastel_palettes.png"
    },
    "roselia.csv": {
        "name": "Roselia",
        "color": "#3344AA",
        "logo": "roselia.png"
    },
    "hello_happy_world.csv": {
        "name": "Hello, Happy World!",
        "color": "#FFCC11",
        "logo": "hello_happy_world.png"
    },
    "ras.csv": {
        "name": "RAISE A SUILEN",
        "color": "#33EEFF",
        "logo": "ras.svg"
    },
    "morfonica.csv": {
        "name": "Morfonica",
        "color": "#5566BB",
        "logo": "morfonica.webp"
    },
    "mygo.csv": {
        "name": "MyGO!!!!!",
        "color": "#4682B4",
        "logo": "mygo.webp"
    },
    "ave.csv": {
        "name": "Ave Mujica",
        "color": "#8A2BE2",
        "logo": "ave.webp"
    },
    "yumemita.csv": {
        "name": "夢限大みゅーたいぷ",
        "color": "#FF69B4",
        "logo": "yumemita.webp"
    },
}

# ---------------------------------------------------------
# 문자열 정규화 및 단순화 함수
# ---------------------------------------------------------
def normalize_and_simplify(text):
    if not isinstance(text, str): 
        return ""
    
    # 전각 문자를 반각으로 정규화
    normalized_text = unicodedata.normalize('NFKC', text)
    
    # 정규표현식으로 단어 문자 및 다국어만 남기고 모두 제거
    clean_text = re.sub(r'[^\w가-힣ぁ-んァ-ヶ一-龥]', '', normalized_text)
    
    return clean_text.lower().strip()

# ---------------------------------------------------------
# HTML 템플릿
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
            --logo-height: 120px;
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
            position: relative;
        }}
        .nav-header {{
            background: #fff;
            border-bottom: 1px solid #f1f1f1;
            padding: 20px 25px;
        }}
        .last-update {{
            font-size: 11px;
            color: #aaa;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
            text-align: right;
        }}
        
        .tab-group {{ 
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }}
        .tab-button {{
            padding: 10px 5px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid #eee;
            background: #fafafa;
            cursor: pointer;
            transition: all 0.2s ease;
            color: #888;
            border-radius: 12px;
            text-align: center;
            word-break: keep-all;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
        }}
        .tab-button:hover {{ background-color: #f0f0f0; color: #333; }}
        .tab-button.active {{
            background-color: #333;
            color: #fff;
            border-color: #333;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .band-logo-area {{ 
            text-align: center; 
            padding: 30px 0 20px 0;
            height: var(--logo-height); 
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .band-logo-area img {{
            height: 100%;
            width: auto;
            max-width: 90%;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }}
        .band-logo-area h1 {{
            margin: 0;
            font-size: 2em;
            color: #333;
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
        
        .song-info-wrapper {{ 
            display: flex; align-items: center; min-width: 200px; padding: 5px;
            border-radius: 8px; transition: background-color 0.2s;
        }}
        .clickable-song {{ cursor: pointer; }}
        .clickable-song:hover {{ background-color: #f1f3f5; }}
        .clickable-song:active {{ background-color: #e9ecef; transform: scale(0.99); }}

        .album-thumb {{
            width: 52px; height: 52px; border-radius: 8px; object-fit: cover;
            margin-right: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex-shrink: 0; background-color: #eee;
        }}
        .song-text {{ display: flex; flex-direction: column; }}
        .song-title-main {{ font-size: 1.05em; font-weight: 700; color: #333; margin-bottom: 2px; }}
        .song-title-sub {{ font-size: 0.8em; color: #999; }}
        
        .meta-info {{ display: flex; flex-direction: column; gap: 4px; font-size: 12px; min-width: 100px; }}
        .meta-top {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .release-date {{ color: #888; font-family: monospace; letter-spacing: -0.5px; }}
        .meta-desc {{ color: #666; font-size: 11px; }}
        .badge {{ padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 800; text-transform: uppercase; display: inline-block; }}
        .badge-original {{ background-color: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }}
        .badge-cover {{ background-color: #fff3e0; color: #f57c00; border: 1px solid #ffe0b2; }}
        .badge-tieup {{ background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }}
        
        .btn {{
            display: inline-flex; align-items: center; justify-content: center;
            text-decoration: none; font-weight: 600; padding: 6px 12px;
            border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; white-space: nowrap;
        }}
        .btn-link {{ background-color: #f1f3f5; color: #495057; }}
        .btn-link:hover {{ background-color: #e9ecef; color: #212529; }}
        
        .source-container {{ margin-top: 30px; padding-top: 15px; border-top: 1px dashed #eee; text-align: center; }}
        .source-link-btn {{
            display: inline-block; padding: 5px 12px; background-color: #f1f3f5;
            color: #868e96; text-decoration: none; border-radius: 15px; font-size: 11px; font-weight: 500;
        }}
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
        .modal-body {{ 
            padding: 30px; 
            overflow-y: auto;
            line-height: 1.8; white-space: pre-wrap; font-size: 16px; text-align: center; color: #444; 
        }}
        .close-btn {{ font-size: 28px; cursor: pointer; border: none; background: none; color: #ccc; }}
        
        /* 우측 하단 고정 버튼 */
        .fixed-guide-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 90px;
            background: linear-gradient(135deg, #FF55BB, #33EEFF);
            color: white;
            padding: 12px 15px;
            border-radius: 12px;
            text-decoration: none;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            transition: transform 0.2s, box-shadow 0.2s;
            text-align: center;
            z-index: 2000;
            line-height: 1.4;
            display: block;
        }}
        .fixed-guide-btn:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.35);
        }}
        .fixed-guide-btn::after {{
            content: "💡";
            display: block;
            font-size: 16px;
            margin-top: 4px;
        }}

        @media (max-width: 600px) {{
            th {{ display: none; }}
            .tab-group {{ grid-template-columns: repeat(3, 1fr); }}
            .fixed-guide-btn {{ bottom: 15px; right: 15px; width: 70px; font-size: 10px; padding: 10px; }}
            :root {{ --logo-height: 100px; }}
        }}
    </style>
</head>
<body>

<a href="https://gall.dcinside.com/mgallery/board/view/?id=bang_dream&no=5985966" target="_blank" class="fixed-guide-btn">
    초심자용<br>뱅드림 뷰잉<br>10밴드 핵심콜
</a>

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
        var modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = scriptEl.innerHTML;
        
        var modalOverlay = document.getElementById('lyrics-modal');
        modalOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        modalBody.scrollTop = 0;
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

# ---------------------------------------------------------
# 파일 매핑 초기화
# ---------------------------------------------------------
file_map = {}
if os.path.exists(LYRICS_FOLDER):
    print("가사 파일 시스템 읽기 완료. 매칭 키를 생성합니다...")
    for f in os.listdir(LYRICS_FOLDER):
        if f.endswith('.txt'):
            base_name = f[:-4]
            match = re.search(r'(_\d+)$', base_name)
            if match:
                suffix = match.group(1)
                real_base = base_name[:-len(suffix)]
                key = normalize_and_simplify(real_base) + suffix
            else:
                key = normalize_and_simplify(base_name)
            file_map[key] = f

print("파일 맵핑 완료. CSV 데이터 처리를 시작합니다.")

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

    def create_link_btn(url):
        if pd.isna(url) or not str(url).strip().startswith("http"): 
            return ""
        return f'<a href="{url}" target="_blank" class="btn btn-link">Listen</a>'

    if "링크" in df.columns:
        df["링크"] = df["링크"].apply(create_link_btn)

    song_column_data = []
    
    for idx, row in df.iterrows():
        title_jp = str(row.get('제목(원어)', '')).strip()
        title_kr = str(row.get('제목(한국어)', '')).strip()
        cover_url = row.get('앨범커버')
        ext_link = row.get('번역가사 링크')

        title_counts[title_jp] = title_counts.get(title_jp, 0) + 1
        suffix = f"_{title_counts[title_jp]}" if title_counts[title_jp] > 1 else ""
        
        search_key = normalize_and_simplify(title_jp) + suffix
        
        script_html = ""
        onclick_attr = ""
        wrapper_class = "song-info-wrapper"
        
        if search_key in file_map:
            actual_filename = file_map[search_key]
            filepath = os.path.join(LYRICS_FOLDER, actual_filename)
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().replace('\\r', '').replace('\\n', '<br>').replace('\r\n', '<br>').replace('\n', '<br>')
                    
                if pd.notna(ext_link) and str(ext_link).strip().startswith("http"):
                    source_btn_html = f'<div class="source-container"><a href="{ext_link}" target="_blank" class="source-link-btn">출처</a></div>'
                    content += source_btn_html
                
                # 자바스크립트 충돌 방지용 규칙
                safe_title = title_jp.replace("\\", "\\\\").replace("'", "\\'").replace('"', '&quot;')
                unique_id = f"{index}_{idx}"
                script_html = f'<script id="lyrics-{unique_id}" type="text/template">{content}</script>'
                onclick_attr = f'onclick="showLyrics(\'{unique_id}\', \'{safe_title}\')"'
                wrapper_class += " clickable-song"
            except Exception as e:
                print(f"가사 파일 열기 실패 ({actual_filename}): {e}")

        text_html = f'<div class="song-text"><span class="song-title-main">{title_jp}</span>'
        if title_kr and title_kr != "nan":
            text_html += f'<span class="song-title-sub">{title_kr}</span>'
        text_html += '</div>'
        
        if pd.notna(cover_url) and isinstance(cover_url, str) and cover_url.strip() != "":
            img_html = f'<img src="{cover_url}" class="album-thumb" alt="cover">'
        else:
            img_html = '<div class="album-thumb" style="background:#f0f0f0;"></div>'
            
        final_cell_html = f'<div class="{wrapper_class}" {onclick_attr}>{img_html}{text_html}</div>{script_html}'
        song_column_data.append(final_cell_html)

    df["곡명"] = song_column_data

    final_df = df[["곡명", "상세정보", "링크"]]
    table_html = final_df.to_html(index=False, escape=False, border=0)
    
    tab_id = f"tab-{index}"
    tabs_html += f'<button class="tab-button" onclick="openTab(event, \'{tab_id}\')">{info["name"]}</button>'
    
    logo_html = f'<img src="{info.get("logo", "")}" alt="{info["name"]}">' if info.get("logo") else f'<h1>{info["name"]}</h1>'
    tables_html += f'<div id="{tab_id}" class="content"><div class="band-logo-area">{logo_html}</div><div class="table-wrapper">{table_html}</div></div>'

final_output = html_template.format(today_date=TODAY_DATE, tab_buttons=tabs_html, table_contents=tables_html)

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
    f.write(final_output)

print("출력 파일 생성 성공했습니다.")