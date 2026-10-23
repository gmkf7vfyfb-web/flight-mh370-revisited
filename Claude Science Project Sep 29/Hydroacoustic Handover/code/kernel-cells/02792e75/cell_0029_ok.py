bbox="100,-26.5,102.5,-25"
tests={"cmr":("https://cmr.earthdata.nasa.gov/search/collections.json",{"keyword":"Landsat 8 OLI","page_size":5}),
"cdse":("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",{"$filter":"Collection/Name eq 'SENTINEL-1' and ContentDate/Start gt 2014-04-01T00:00:00.000Z and ContentDate/Start lt 2014-04-02T00:00:00.000Z","$top":"2"}),
"usgs_m2m":("https://m2m.cr.usgs.gov/api/api/json/stable/",{}),
"stac_es":("https://earth-search.aws.element84.com/v1/collections",{}),
"pc":("https://planetarycomputer.microsoft.com/api/stac/v1/collections",{})}
for k,(u,p) in tests.items():
    try:
        r=requests.get(u,params=p,timeout=40); print(k,r.status_code,len(r.content), r.text[:150].replace("\n"," "))
    except Exception as e: print(k,"ERR",str(e)[:150])