
import urllib.request, re, urllib.parse
def get(u, t=90):
    with urllib.request.urlopen(u, timeout=t) as r: return r.read().decode("utf8","ignore")
h = get("https://www.mot.gov.my/en/")
cand = sorted(set(re.findall(r'href="([^"]*)"', h)))
mh = [c for c in cand if re.search(r'(mh370|mh%20370|laporan|aviation)', c, re.I)]
print(mh[:40])
