CMR="https://cmr.earthdata.nasa.gov/search"
tq="2014-03-08T00:00:00Z,2014-04-30T23:59:59Z"
def colls(kw):
    r=requests.get(CMR+"/collections.json",params={"keyword":kw,"bounding_box":bbox,"temporal":tq,"page_size":50},timeout=60)
    return [(c["short_name"],c.get("version_id"),c["id"],c.get("data_center")) for c in r.json()["feed"]["entry"]]
for kw in ["Landsat","ASTER L1T","EO-1","MOD02QKM","MYD02QKM","VIIRS SDR imagery","Sentinel-1"]:
    try: cs=colls(kw); print(kw,len(cs),cs[:8])
    except Exception as e: print(kw,e)