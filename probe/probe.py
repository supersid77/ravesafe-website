import re, urllib.request, time
def get(u, ua):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":ua}),timeout=25); return r.read().decode("utf-8","replace"), dict(r.headers)
def body_id(h):
    m=re.search(r'id="sample-data-results(\d+)"',h); t=re.search(r'nhsuk-heading-m">([^<]*)<',h); p=re.search(r'Purchase intent</th>\s*<td[^>]*>\s*([^<]*?)\s*<',h)
    return (m and m.group(1), t and t.group(1), p and p.group(1))
for ua in ["Mozilla/5.0 (RaveSafe feed check; +https://ravesafecommunity.com)","Mozilla/5.0 (compatible; RaveSafe Community data log; +https://ravesafecommunity.com; miss.k@ravesafecommunity.com)","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"]:
    for u in ["https://wedinos.wales/sample/w106245/","https://wedinos.wales/sample/w106374/","https://www.wedinos.wales/sample/w106374/"]:
        try:
            h,hd=get(u,ua); print(ua[:40],"|",u[-25:],"|",body_id(h),"| cache:",hd.get("X-Cache") or hd.get("x-cache") or hd.get("CF-Cache-Status") or hd.get("Age"))
        except Exception as e: print(ua[:40],u,"ERR",e)
        time.sleep(1)
h,_=get("https://wedinos.wales/sample/","Mozilla/5.0 (RaveSafe feed check)")
print("=== endpoints on /sample/:", sorted(set(re.findall(r'(wp-json/[^"\'\s<>]+|admin-ajax\.php[^"\'\s<>]*|action["\']?\s*[:=]\s*["\'][a-z_]+)',h)))[:30])
print("=== forms:", re.findall(r'<form[^>]*>',h)[:5])
