poly="POLYGON((100 -26.5,102.5 -26.5,102.5 -25,100 -25,100 -26.5))"
res={}
# Copernicus: all collections, 2014-03-08 .. 2014-05-31
def cdse(coll,t0="2014-03-08T00:00:00.000Z",t1="2014-06-01T00:00:00.000Z",aoi=poly):
    f=f"Collection/Name eq '{coll}' and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {t0} and ContentDate/Start lt {t1}"
    r=requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",params={"$filter":f,"$top":"200","$orderby":"ContentDate/Start asc"},timeout=90)
    return r.status_code, r.json().get("value",[]) if r.ok else r.text[:300]
for coll in ["SENTINEL-1","SENTINEL-2","SENTINEL-3","LANDSAT-8","LANDSAT-7","ENVISAT","SMOS","TERRAAQUA","COP-DEM"]:
    try:
        sc,v=cdse(coll); res[coll]=v; print(coll,sc,len(v) if isinstance(v,list) else v)
    except Exception as e: print(coll,"ERR",str(e)[:200])