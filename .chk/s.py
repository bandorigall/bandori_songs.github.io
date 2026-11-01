import re,sys,time,urllib.request,urllib.parse
for k in sys.argv[1:]:
    time.sleep(3)
    u="https://gall.dcinside.com/mgallery/board/lists/?id=bang_dream&s_type=search_subject_memo&s_keyword="+urllib.parse.quote(k)
    h=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"})).read().decode('utf-8','ignore')
    print('==',k,'captcha','사람인지 확인' in h)
    for m in re.finditer(r'data-no="(\d+)".*?gall_tit[^>]*>(.*?)</td>.*?gall_date[^>]*title="([^"]+)"',h,re.S):
        print(m.group(1),m.group(3),re.sub(r'<[^>]+>|\s+',' ',m.group(2)).strip()[:80])
