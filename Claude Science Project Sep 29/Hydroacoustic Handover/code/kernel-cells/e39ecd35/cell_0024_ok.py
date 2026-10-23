
import urllib.request, re
html=""
for u in ["https://www.atsb.gov.au/mh370-pages/reports","https://www.atsb.gov.au/mh370","https://www.atsb.gov.au/about-search"]:
    try:
        with urllib.request.urlopen(u, timeout=90) as r: h=r.read().decode("utf8","ignore")
        html+=h
        print("OK",u,len(h))
    except Exception as e: print("FAIL",u,type(e).__name__,str(e)[:120])
links = sorted(set(re.findall(r'href="([^"]+\.pdf)"', html)))
for l in links: print(l)
