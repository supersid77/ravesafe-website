import re, urllib.request
ua={"User-Agent":"Mozilla/5.0 (RaveSafe feed check; +https://ravesafecommunity.com)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=ua),timeout=25).read().decode("utf-8","replace")
h=get("https://checkit.wien/drug-checking-ergebnisse/")
i=h.find("Aktuelle Warnungen und Besonderheiten")
print("=== checkit html around list"); print(h[i:i+6000])
print("=== checkit sitemap/feeds"); 
for u in ["https://checkit.wien/wp-json/wp/v2/posts?per_page=3&_fields=date,link,title","https://checkit.wien/category/warnungen/feed/","https://checkit.wien/robots.txt"]:
    try: print(u, get(u)[:1200])
    except Exception as e: print(u,"ERR",e)
f=get("https://energycontrol.org/alertas/feed/")
print("=== EC items", len(re.findall("<item>",f))); print(re.findall(r"<link>(.*?)</link>",f)[:4]); print(re.findall(r"<language>(.*?)</language>",f))
