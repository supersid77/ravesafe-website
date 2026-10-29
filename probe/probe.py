import re, sys, urllib.request, ssl
ua={"User-Agent":"Mozilla/5.0 (RaveSafe feed check; +https://ravesafecommunity.com)"}
for u in open("probe/urls.txt").read().split():
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=ua),timeout=20)
        b=r.read(400000); t=b.decode("utf-8","replace")
        ct=r.headers.get("content-type","")
        feeds=set(re.findall(r'<link[^>]+type="application/(?:rss|atom)\+xml"[^>]*href="([^"]+)"',t))
        items=len(re.findall(r"<item[ >]",t))+len(re.findall(r"<entry[ >]",t))
        titles=re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>",t)[:4]
        dates=re.findall(r"<pubDate>(.*?)</pubDate>",t)[:2]
        print(f"OK {r.status} {u}\n   type={ct} bytes={len(b)} items={items} feeds={sorted(feeds)[:5]}\n   titles={titles}\n   dates={dates}")
        if "json" in ct: print("   json:",t[:600].replace("\n"," "))
    except Exception as e:
        print(f"FAIL {u} {type(e).__name__}: {str(e)[:120]}")
