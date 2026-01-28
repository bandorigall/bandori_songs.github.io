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

# 밴드별 설정 (로고 파일명 확인 필요)
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
        "name": "Yumemita",
        "color": "#FF69B4", 
        "bg_color": "rgba(255, 105, 180, 0.05)",
        "logo": "yumemita.webp"
    },
}

# ---------------------------------------------------------
# HTML 템플릿
# ---------------------------------------------------------
html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bang Dream Setlist</title>
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

        .tab-group {{ display: flex; }}

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

        .song-info-wrapper {{ display: flex; align-items: center; min-width: 280px; }}
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
        .song-title-main {{ font-size: 1.1em; font-weight: 700; color: #333; margin-bottom: 2px; }}
        .song-title-sub {{ font-size: 0.85em; color: #999; }}

        .meta-info {{ display: flex; flex-direction: column; gap: 4px; font-size: 12px; }}
        .meta-top {{ display: flex; align-items: center; gap: 8px; }}
        .release-date {{ color: #888; font-family: monospace; letter-spacing: -0.5px; }}
        .meta-desc {{ color: #666; font-size: 11px; }}

        /* 배지 스타일 */
        .badge {{ padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .badge-original {{ background-color: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }}
        .badge-cover {{ background-color: #fff3e0; color: #f57c00; border: 1px solid #ffe0b2; }}

        .btn {{
            display: inline-flex; align-items: center; justify-content: center;
            text-decoration: none; font-weight: 600; padding: 6px 12px;
            border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; border: none; white-space: nowrap;
        }}
        .btn-link {{ background-color: #f1f3f5; color: #495057; }}
        .btn-link:hover {{ background-color: #e9ecef; color: #212529; }}
        .btn-lyrics {{ background-color: #fff0f6; color: #d63384; }}
        .btn-lyrics:hover {{ background-color: #fcc2d7; color: #a61e4d; }}
        .btn-disabled {{ opacity: 0.4; cursor: default; }}

        .footer {{
            margin-top: auto;
            font-size: 11px;
            color: #ccc;
            text-align: center;
            padding-bottom: 10px;
        }}

        .modal-overlay {{
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(5px); z-index: 1000;
        }}
        .modal-box {{
            position: relative; background: #fff; width: 90%; max-width: 500px;
            margin: 8% auto; border-radius: 20px; max-height: 80vh;
            display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .modal-header {{
            padding: 20px 25px; border-bottom: 1px solid #f0f0f0;
            display: flex; justify-content: space-between; align-items: center;
        }}
        .modal-body {{
            padding: 30px; overflow-y: auto; line-height: 1.8;
            white-space: pre-wrap; font-size: 16px; text-align: center; color: #444;
        }}
        .close-btn {{ font-size: 28px; cursor: pointer; border: none; background: none; color: #ccc; }}
        .close-btn:hover {{ color: #333; }}
    </style>
</head>
<body>

<div class="container">
    <div class="nav-header">
        <div class="last-update">Last Update: {today_date}</div>
        <div class="tab-group" id="tab-nav">
            {tab_buttons}
        </div>
    </div>
    {table_contents}
</div>

<div class="footer">
    made by Bangbung Kim
</div>

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
    
    document.addEventListener('keydown', function(event) {{
        if (event.key === "Escape") closeModal();
    }});

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
        # 데이터 읽기
        df = pd.read_csv(file)
        
        # 컬럼 이름 공백 제거 (혹시 모를 오류 방지)
        df.columns = df.columns.str.strip()
        
    except FileNotFoundError:
        print(f"파일 없음: {file}")
        continue

    # 1. 원어 제목 리스트 (가사 파일 매칭용) - CSV의 '제목(원어)' 컬럼
    original_titles = df.get('제목(원어)').tolist()

    # 2. 곡 정보 통합 (제목(원어)가 위, 제목(한국어)가 아래)
    def merge_cover_and_title(row):
        title_jp = str(row.get('제목(원어)', '')).strip() # 메인 타이틀 (위)
        title_kr = str(row.get('제목(한국어)', '')).strip() # 서브 타이틀 (아래)
        
        # 텍스트 HTML (줄바꿈 기호 없이 한 줄로 작성하여 깨짐 방지)
        text_html = f'<div class="song-text"><span class="song-title-main">{title_jp}</span>'
        if title_kr and title_kr != "nan":
            text_html += f'<span class="song-title-sub">{title_kr}</span>'
        text_html += '</div>'
        
        # 앨범커버 HTML
        cover_url = row.get('앨범커버')
        if pd.notna(cover_url) and isinstance(cover_url, str) and cover_url.strip() != "":
            img_html = f'<a href="{cover_url}" target="_blank"><img src="{cover_url}" class="album-thumb" alt="cover"></a>'
        else:
            img_html = '<div class="album-thumb" style="background:#f0f0f0;"></div>'
        
        return f'<div class="song-info-wrapper">{img_html}{text_html}</div>'

    df["곡명"] = df.apply(merge_cover_and_title, axis=1)

    # 3. 상세 정보 통합 (배지 및 날짜 한 줄 처리)
    def merge_meta_info(row):
        release_date = str(row.get('발매일 / 커버일', '-')).strip()
        song_type = str(row.get('곡유형', '')).strip()
        orig_artist = str(row.get('원곡가수', '')).strip()

        badge_html = ""
        desc_text = ""

        if "오리지널" in song_type:
            badge_html = '<span class="badge badge-original">ORIGINAL</span>'
        elif "타이업" in song_type:
            badge_html = '<span class="badge badge-original" style="background-color: #e8f5e9; color: #2e7d32; border-color: #c8e6c9;">TIE-UP</span>'
        elif "커버" in song_type:
            badge_html = '<span class="badge badge-cover">COVER</span>'
            if orig_artist and orig_artist != "nan":
                desc_text = f"Original by {orig_artist}"

        # 문자열 내 \n 삽입을 방지하기 위해 구조 재정렬
        meta_html = f'<div class="meta-info"><div class="meta-top">{badge_html}<span class="release-date">{release_date}</span></div>'
        if desc_text:
            meta_html += f'<span class="meta-desc">{desc_text}</span>'
        meta_html += '</div>'
        
        return meta_html

    df["상세정보"] = df.apply(merge_meta_info, axis=1)

    # 4. 가사 및 외부 링크 통합 처리 (Lyrics 주강조, 출처 우측 보조)
    lyrics_column = []
    for idx, title_raw in enumerate(original_titles):
        t_str = str(title_raw).strip()
        title_counts[t_str] = title_counts.get(t_str, 0) + 1
        
        suffix = f"_{title_counts[t_str]}" if title_counts[t_str] > 1 else ""
        filename = f"{t_str}{suffix}.txt"
        filepath = os.path.join(LYRICS_FOLDER, filename)
        unique_id = f"{index}_{idx}"
        
        row_data = df.iloc[idx]
        ext_link = row_data.get('번역가사 링크')
        
        # 버튼들을 감싸는 컨테이너 (중앙 정렬 및 여유 공간)
        btn_group_html = '<div style="display: flex; align-items: center; justify-content: center; gap: 8px;">'
        
        # [A] 팝업 가사 버튼 (메인)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().replace('\\r', '').replace('\\n', '<br>').replace('\r\n', '<br>').replace('\n', '<br>')
            safe_title = html.escape(t_str)
            btn_group_html += f'<button class="btn btn-lyrics" style="padding: 6px 16px; font-size: 13px;" onclick="showLyrics(\'{unique_id}\', \'{safe_title}\')">Lyrics</button>'
            btn_group_html += f'<script id="lyrics-{unique_id}" type="text/template">{content}</script>'
        else:
            btn_group_html += '<span class="btn btn-disabled" style="font-size: 11px;">No Text</span>'

        # [B] 외부 링크 (출처 - 보조 아이콘 스타일)
        if pd.notna(ext_link) and str(ext_link).strip().startswith("http"):
            # 매우 작은 회색 둥근 배지 형태로 Lyrics 옆에 살짝 붙임
            btn_group_html += f'''
            <a href="{ext_link}" target="_blank" 
               style="font-size: 9px; color: #ced4da; text-decoration: none; border: 1px solid #e9ecef; 
                      padding: 2px 5px; border-radius: 4px; line-height: 1;" 
               title="외부 번역 출처로 이동">출처</a>
            '''
        
        btn_group_html += '</div>'
        lyrics_column.append(btn_group_html)

    df["가사"] = lyrics_column
    
    # 5. 링크 버튼 (URL 검증 추가)
    def create_link_btn(url):
        if pd.isna(url) or str(url).strip() == "":
            return ""
        # URL이 'http'로 시작하지 않으면(예: 그냥 텍스트면) 버튼을 만들지 않음
        if not str(url).strip().startswith("http"):
            return "" # 혹은 텍스트로 표시하고 싶으면 return str(url)
        return f'<a href="{url}" target="_blank" class="btn btn-link">Listen</a>'

    if "링크" in df.columns:
        df["링크"] = df["링크"].apply(create_link_btn)

    # 최종 컬럼 선택
    final_df = df[["곡명", "상세정보", "링크", "가사"]]

    # HTML 변환
    table_html = final_df.to_html(index=False, escape=False, border=0)
    
    # 탭 및 로고 생성
    tab_id = f"tab-{index}"
    tabs_html += f'<button class="tab-button" onclick="openTab(event, \'{tab_id}\')">{info["name"]}</button>'
    
    logo_html = f'<img src="{info.get("logo", "")}" alt="{info["name"]}">' if info.get("logo") else f'<h1>{info["name"]}</h1>'
    
    tables_html += f"""
    <div id="{tab_id}" class="content">
        <div class="band-logo-area">{logo_html}</div>
        <div class="table-wrapper">{table_html}</div>
    </div>
    """
    print(f"{info['name']} 처리 완료")

# 최종 저장
final_output = html_template.format(
    today_date=TODAY_DATE,
    tab_buttons=tabs_html, 
    table_contents=tables_html
)

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
    f.write(final_output)

print(f"\n🎉 {OUTPUT_FILENAME} 생성 완료! CSV 구조에 맞게 수정되었습니다.")