t=texts["atsb2017_text.txt"][0]
pages=[(m.start(),int(m.group(1))) for m in re.finditer(r"› (\d+) ‹",t)]
def pg(pos):
    p=None
    for s,n in pages:
        if s<=pos: p=n
        else: break
    return p
hits=[]
for m in re.finditer(r"(?i)satellite imag|Geospatial|AGO\b|imagery|DigitalGlobe|Pleiades|PLEIADES|TerraSAR|COSMO|RADARSAT|Gaofen|THEOS|Thaichote",t):
    hits.append((pg(m.start()),m.group(0),m.start()))
from collections import defaultdict
d=defaultdict(list)
for p,g,s in hits: d[p].append(g)
print({k:len(v) for k,v in sorted(d.items(), key=lambda x:(x[0] or 0))})
# also S1 locality other modes
for k,c in [("S1A GRD","C1214470533-ASF"),("S1A SLC","C1214470488-ASF")]:
    print(k,gran_b(c,bbox,"2014-04-01T00:00:00Z,2015-12-31T23:59:59Z"))