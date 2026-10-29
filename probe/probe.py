import re, json, urllib.request
ua={"User-Agent":"Mozilla/5.0 (RaveSafe data check; +https://ravesafecommunity.com)"}
def get(u): 
    r=urllib.request.urlopen(urllib.request.Request(u,headers=ua),timeout=25); return r.read().decode("utf-8","replace"), dict(r.headers)
h,_=get("https://wedinos.wales/sample/w106245/")
i=h.find("Date received")
print("=== sample html"); print(h[max(0,i-1500):i+5000])
print("=== another sample text")
h2,_=get("https://wedinos.wales/sample/w106298/")
print(re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",h2[h2.find("Date received")-50:h2.find("Date received")+1500])))
d,hd=get("https://www.wedinos.wales/wp-json/wp/v2/sample?per_page=1&_fields=id,date,link")
print("=== totals", hd.get("X-WP-Total"), hd.get("X-WP-TotalPages"))
d,hd=get("https://www.wedinos.wales/wp-json/wp/v2/sample?per_page=1&_fields=id,date,link&after=2026-07-29T00:00:00")
print("=== since 29 Jul", hd.get("X-WP-Total"))
d,hd=get("https://www.wedinos.wales/wp-json/wp/v2/sample?per_page=1&_fields=id,date,link&after=2025-10-29T00:00:00")
print("=== since 29 Oct 2025", hd.get("X-WP-Total"))
print("=== taxonomies"); print(get("https://www.wedinos.wales/wp-json/wp/v2/types/sample")[0][:800])
