STAC="https://landsatlook.usgs.gov/stac-server/search"
def lsearch(bb,dt,coll=["landsat-c2l1"]):
    r=requests.post(STAC,json={"bbox":bb,"datetime":dt,"collections":coll,"limit":200},timeout=120)
    j=r.json(); return r.status_code, j.get("numberMatched", len(j.get("features",[]))), [(f["id"],f["properties"].get("datetime")) for f in j.get("features",[])[:5]]
print("control Perth", lsearch([115,-33,117,-31],"2014-03-08T00:00:00Z/2014-04-30T23:59:59Z"))
print("locality 8Mar-30Apr2014", lsearch([100,-26.5,102.5,-25],"2014-03-08T00:00:00Z/2014-04-30T23:59:59Z"))
print("locality 2013-2026", lsearch([100,-26.5,102.5,-25],"2013-01-01T00:00:00Z/2026-10-01T00:00:00Z"))
print("wider 95-108E 20-32S Mar-Apr 2014", lsearch([95,-32,108,-20],"2014-03-08T00:00:00Z/2014-04-30T23:59:59Z"))