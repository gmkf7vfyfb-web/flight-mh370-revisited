import requests, html, time
rows=[l.split() for l in open("src/cdx.txt").read().splitlines() if l.strip()]
want={}
for u,ts in rows:
    m=re.search(r"/(mr0\d\d)\.aspx$",u)
    if m and int(m.group(1)[2:])<=27: want[m.group(1)]=(u,ts)
os.makedirs("src/jacc",exist_ok=True)
def strip(h):
    h=re.sub(r"(?is)<(script|style).*?</\1>","",h)
    body=re.search(r"(?is)<div[^>]+id=\"?(content|main)[^>]*>(.*)",h)
    t=re.sub(r"(?s)<[^>]+>"," ",h); t=html.unescape(t); t=re.sub(r"[ \t\r\f\v]+"," ",t); t=re.sub(r"\n\s*\n+","\n",t)
    return t
jacc={}
for k,(u,ts) in sorted(want.items()):
    url=f"http://web.archive.org/web/{ts}id_/{u}"
    try:
        r=requests.get(url,timeout=60); t=strip(r.text); jacc[k]=(ts,u,t)
        open(f"src/jacc/{k}.txt","w").write(f"{url}\n{t}")
    except Exception as e: print(k,e)
for k,(ts,u,t) in jacc.items():
    title=re.search(r"(?i)(MH370[^\n]{0,120})",t)
    print(k,ts,len(t),"Haixun" in t, "white" in t.lower(), (title.group(1)[:90] if title else ""))