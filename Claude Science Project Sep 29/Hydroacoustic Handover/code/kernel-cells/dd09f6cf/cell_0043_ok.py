import re, collections, datetime as dt
S=json.load(open(host.artifact_path('a74cc2b4-988c-4dad-95ff-468f16dfeaff')))
feats=S['features']; print(len(feats), feats[0]['properties'], feats[0]['geometry']['type'])
names=collections.Counter(f['properties']['Name'] for f in feats); print(list(names.items())[:12])
# polygons covering crossing and Haixun
from shapely.geometry import shape
polys=[]
for f in feats:
    nm=f['properties']['Name']; mday=re.match(r'D(\d+)',nm)
    g=make_valid(shape(f['geometry'])); polys.append((nm,int(mday.group(1)) if mday else None,g))
for lab,pt in P.items():
    hits=[(nm,dn,(dt.date(2014,3,7)+dt.timedelta(days=dn)).isoformat()) for nm,dn,g in polys if g.contains(pt)]
    print(lab, hits)
print(set(type(d) for _,d,_ in polys), min(d for _,d,_ in polys), max(d for _,d,_ in polys))