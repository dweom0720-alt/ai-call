# 알라딘 연도별 베스트셀러·스테디셀러 목록으로 한국어 책 목록(제목·저자·연도)을 만든다 → covers/catalog.json
import re, json, time, urllib.request, urllib.parse, html, sys
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","Accept-Language":"ko-KR,ko;q=0.9"}
def get(u):
    for t in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r: return r.read().decode("utf-8","ignore")
        except Exception as e: time.sleep(2)
    return ""
ITEM=re.compile(r'<a href="[^"]*wproduct\.aspx\?ItemId=(\d+)[^"]*" class="bo3"><b>(.*?)</b></a>(.*?)</li>\s*<li>(.*?)</li>',re.S)
def parse(h):
    out=[]
    for m in ITEM.finditer(h):
        iid,title,sub,info=m.groups()
        title=html.unescape(re.sub(r"<.*?>","",title)).strip()
        auth=re.findall(r'AuthorSearch=[^"]*">(.*?)</a>',info)
        auth=html.unescape(re.sub(r"<.*?>","",auth[0])).strip() if auth else ""
        y=re.search(r'(\d{4})년',info)
        out.append([title,auth,y.group(1) if y else "",iid])
    return out
mode=sys.argv[1] if len(sys.argv)>1 else "full"
seen={};order=[]
def add(items):
    for t,a,y,i in items:
        k=re.sub(r"\s","",t)+"|"+a
        if k not in seen: seen[k]=1;order.append([t,a,y])
urls=[]
for page in range(1,21): urls.append(f"https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=SteadySeller&BranchType=1&CID=0&page={page}&cnt=1000&SortOrder=1")
for year in range(2026,1999,-1):
    for page in range(1,21 if mode=="full" else 2):
        urls.append(f"https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=YearlyBest&BranchType=1&CID=0&Year={year}&page={page}&cnt=1000&SortOrder=1")
if mode=="probe": urls=urls[:1]+[u for u in urls if "Year=2012" in u][:1]
for n,u in enumerate(urls):
    h=get(u);items=parse(h)
    if mode=="probe":
        open("covers/probe.html","w").write(h[:400000]);print(u,len(h),len(items),items[:5])
    add(items)
    if n%20==0: print(n,len(urls),len(order),flush=True)
    time.sleep(0.4)
json.dump(order,open("covers/catalog.json","w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print("total",len(order))
