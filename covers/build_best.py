# 알라딘 주간 베스트셀러(종합·분야별 상위 30)를 covers/best.json 으로 저장
import re, json, time, urllib.request, html, datetime
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"ko-KR,ko;q=0.9"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r: return r.read().decode("utf-8","ignore")
ITEM=re.compile(r'<a href="[^"]*wproduct\.aspx\?ItemId=(\d+)" class="bo3">(?:<b>)?(.*?)(?:</b>)?</a>(.*?)</li>\s*<li>(.*?)</li>',re.S)
CATS=[("all","종합",0),("biz","경제경영",170),("human","인문",656),("self","자기계발",336),("essay","에세이",55889),("novel","소설",1),("sci","과학",987)]
out=[]
for i,(k,name,cid) in enumerate(CATS):
    items=[];period=""
    for page in (1,2):
        h=get(f"https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID={cid}&page={page}&cnt=1000&SortOrder=1")
        if not period:
            m=re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d)주',h)
            if m: period=f"{m.group(1)}년 {m.group(2)}월 {m.group(3)}주"
        for iid,title,sub,info in ITEM.findall(h):
            t=html.unescape(re.sub(r"<.*?>","",title)).strip()
            au=re.findall(r'AuthorSearch=[^"]*">(.*?)</a>',info);pub=re.findall(r'PublisherSearch=[^"]*"\s*>(.*?)</A>',info,re.I)
            sub=html.unescape(re.sub(r"<.*?>","",sub)).strip(" -\xa0")
            items.append({"rank":len(items)+1,"title":t,"author":html.unescape(re.sub(r"<.*?>","",au[0])).strip() if au else "","publisher":html.unescape(pub[0]).strip() if pub else "","note":sub[:80]})
            if len(items)>=30: break
        if len(items)>=30: break
        time.sleep(0.5)
    out.append({"id":"al_"+k,"store":name,"order":i+1,"period":period or "이번 주","asOf":datetime.date.today().isoformat(),"source":f"https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID={cid}","sourceName":"알라딘 주간 베스트셀러","items":items})
    print(name,len(items),period,items[:2])
json.dump(out,open("covers/best.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
