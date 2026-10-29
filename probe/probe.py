import re, urllib.request, time, html, json
UA={"User-Agent":"Mozilla/5.0 (RaveSafe data check; +https://ravesafecommunity.com)"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25); b=r.read(); return b, r.headers.get("content-type","")
def txt(h): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",re.sub(r"(?s)<(script|style|nav|footer)[^>]*>.*?</\1>","",h))))
def show(name,u,n=1200,raw=False):
    print("\n=====",name,u)
    try:
        b,ct=get(u); h=b.decode("utf-8","replace"); print("type",ct,"bytes",len(b))
        apis=sorted(set(re.findall(r'["\'](https?://[^"\']*(?:api|json|graphql|\.json)[^"\']*)["\']',h)))[:12]
        if apis: print("api-like urls:",apis)
        print(h[:n] if raw else txt(h)[:n])
    except Exception as e: print("ERR",e)
    time.sleep(1)
show("Saferparty warnings page","https://www.saferparty.ch/warnungen",600)
show("Saferparty next data","https://www.saferparty.ch/_next/data",300)
b,_=get("https://www.saferparty.ch/warnungen"); h=b.decode("utf-8","replace")
print("saferparty scripts:",re.findall(r'<script[^>]+src="([^"]+)"',h)[:15])
print("saferparty __NEXT_DATA__:", "__NEXT_DATA__" in h, " nuxt:", "__NUXT__" in h)
m=re.search(r'(?s)<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',h)
if m: print(m.group(1)[:2500])
show("Infodrog warnings","https://www.infodrog.ch/de/aktivitaeten/safer-nightlife/warnungen.html",1500)
show("Infodrog warnings (fr)","https://www.infodrog.ch/fr/activites/safer-nightlife/alertes.html",600)
show("Rave it Safe Bern","https://www.raveitsafe.ch/warnungen/",1200)
show("Drugchecking Berlin","https://drugchecking.berlin/",1200)
show("Drugchecking Berlin warnungen","https://drugchecking.berlin/warnungen",1200)
show("checkit PDF list (warnungen archive)","https://checkit.wien/warnungen/",800)
show("Energy Control alert page","https://energycontrol.org/alertas/alerta-en-espana-pmma-y-mdma-en-pastillas-vendidas-como-mdma/",1500)
show("Kosmicare","https://www.kosmicare.org/",500)
show("Trimbos red alerts","https://www.trimbos.nl/actueel/?s=waarschuwing",500)
show("TEDI feed","https://tedinetwork.org/feed/",500,raw=True)
show("Know Drugs","https://knowdrugs.app/",500)
show("Pill reports eu","https://www.drugsandme.org/",300)
