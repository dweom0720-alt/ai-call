# 생각서재 책 표지 가져오기: covers/request.json 의 책마다 알라딘 → 예스24 → 구글북스 순으로 표지를 찾아 covers/out/<id>.jpg 로 저장
import json, re, sys, urllib.parse, urllib.request, io, os
from PIL import Image
UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36", "Accept-Language": "ko-KR,ko;q=0.9"}
def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        b = r.read()
    return b if binary else b.decode("utf-8", "ignore")
def aladin(q):
    h = get("https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&SearchWord=" + urllib.parse.quote(q))
    m = re.search(r'https://image\.aladin\.co\.kr/product/\d+/\d+/(?:cover\w*|letslook)/[^"\'\s]+?\.(?:jpg|png)', h)
    return re.sub(r'/cover\w*/', '/cover500/', m.group(0)) if m else None
def yes24(q):
    h = get("https://www.yes24.com/Product/Search?domain=BOOK&query=" + urllib.parse.quote(q))
    m = re.search(r'https://image\.yes24\.com/goods/(\d+)/', h)
    return f"https://image.yes24.com/goods/{m.group(1)}/XL" if m else None
def gbooks(q):
    j = json.loads(get("https://www.googleapis.com/books/v1/volumes?maxResults=5&q=" + urllib.parse.quote(q)))
    for it in j.get("items", []):
        il = it.get("volumeInfo", {}).get("imageLinks", {})
        u = il.get("thumbnail") or il.get("smallThumbnail")
        if u: return u.replace("http://", "https://").replace("&edge=curl", "") + "&zoom=1"
    return None
req = json.load(open("covers/request.json", encoding="utf-8"))
os.makedirs("covers/out", exist_ok=True)
result = {}
for b in req["books"]:
    q = (b["title"] + " " + re.sub(r"\(.*?\)", "", b.get("author", "")).replace("엮음", "")).strip()
    for name, fn in (("aladin", aladin), ("yes24", yes24), ("gbooks", gbooks)):
        try:
            u = fn(q) or fn(b["title"])
            if not u: continue
            im = Image.open(io.BytesIO(get(u, True))).convert("RGB")
            if im.width < 60: continue
            sc = min(1, 360 / im.width); im = im.resize((round(im.width * sc), round(im.height * sc)))
            im.save(f"covers/out/{b['id']}.jpg", "JPEG", quality=82)
            result[b["id"]] = {"title": b["title"], "src": name, "url": u}
            break
        except Exception as e:
            print(b["title"], name, "fail", e, file=sys.stderr)
    print(b["title"], "->", result.get(b["id"]))
json.dump(result, open("covers/out/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
