found={}
for kw in ["TerraSAR-X","COSMO-SkyMed","RADARSAT-2","SPOT","Pleiades","KOMPSAT","GeoEye","WorldView","IKONOS","DMC","RapidEye","Gaofen","THEOS"]:
    try:
        r=requests.get(CMR+"/collections.json",params={"keyword":kw,"bounding_box":bbox,"temporal":tq,"page_size":30},timeout=60)
        e=r.json()["feed"]["entry"]; found[kw]=[(c["short_name"][:60],c["id"],c.get("data_center")) for c in e]
        print(kw,len(e),[x[0][:40]+"|"+x[2] for x in found[kw][:6]])
    except Exception as ex: print(kw,"ERR",str(ex)[:100])