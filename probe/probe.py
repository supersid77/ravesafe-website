import re, json, urllib.request, html
ua={"User-Agent":"Mozilla/5.0 (RaveSafe feed check; +https://ravesafecommunity.com)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=ua),timeout=25).read().decode("utf-8","replace")
def text(h): 
    h=re.sub(r"(?s)<(script|style|nav|header|footer)[^>]*>.*?</\1>","",h); return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",h)))
def sec(n): print("\n=====",n)
try:
    sec("WEDINOS sample json (1 record, keys and meta)")
    d=json.loads(get("https://www.wedinos.wales/wp-json/wp/v2/sample?per_page=2"))
    for r in d:
        print({k:(v if k not in("content","_links","yoast_head","yoast_head_json") else "...") for k,v in r.items()})
        print("content:",text(r.get("content",{}).get("rendered",""))[:500])
except Exception as e: print("ERR",e)
for n,u,limit in [("WEDINOS sample page","https://wedinos.wales/sample/w106245/",1500),
 ("WEDINOS sample feed item","https://www.wedinos.wales/sample/feed/",2500),
 ("Energy Control alertas feed","https://energycontrol.org/alertas/feed/",2500),
 ("Energy Control international feed","https://energycontrol-international.org/feed/",1500),
 ("TEDI feed","https://tedinetwork.org/feed/",1500),
 ("Saferparty warnungen text","https://www.saferparty.ch/warnungen",2500),
 ("checkit results text","https://checkit.wien/drug-checking-ergebnisse/",2000),
 ("DrugsData results text","https://www.drugsdata.org/results.php",2000),
 ("Know Your Stuff NZ feed","https://knowyourstuff.nz/feed/",800),
 ("WEDINOS terms","https://www.wedinos.wales/terms-and-conditions/",1500),
 ("WEDINOS robots","https://www.wedinos.wales/robots.txt",500)]:
    sec(n)
    try:
        h=get(u)
        if "feed" in u:
            items=re.findall(r"(?s)<item>(.*?)</item>",h)[:3]
            for it in items:
                t=re.search(r"<title>(.*?)</title>",it); d=re.search(r"<pubDate>(.*?)</pubDate>",it); c=re.findall(r"<category>(.*?)</category>",it)
                desc=re.search(r"(?s)<description>(.*?)</description>",it)
                print("-",t and t.group(1),"|",d and d.group(1),"|",c[:4],"|",text(html.unescape(desc.group(1)) if desc else "")[:300])
        else: print(text(h)[:limit])
    except Exception as e: print("ERR",e)
