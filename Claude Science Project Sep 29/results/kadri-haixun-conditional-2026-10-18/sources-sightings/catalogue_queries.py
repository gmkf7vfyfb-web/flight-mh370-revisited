"""Re-run the public-catalogue checks of the sources-and-sightings leg (18 Oct 2026). Needs network access to
cmr.earthdata.nasa.gov, landsatlook.usgs.gov and catalogue.dataspace.copernicus.eu. No credentials."""
import requests, json
BBOX="100,-26.5,102.5,-25"; T="2014-03-08T00:00:00Z,2014-04-30T23:59:59Z"; CMR="https://cmr.earthdata.nasa.gov/search"
POLY="POLYGON((100 -26.5,102.5 -26.5,102.5 -25,100 -25,100 -26.5))"
CMR_COLL={"MOD02QKM 6.1":"C1378579425-LAADS","MYD02QKM 6.1":"C1379759127-LAADS","ASTER L1T":"C3306888411-LPCLOUD",
 "EO-1 ALI":"C1220566654-USGS_LTA","EO-1 Hyperion":"C1220567951-USGS_LTA","S1A SLC":"C1214470488-ASF","S1A GRD":"C1214470533-ASF",
 "S1A OCN":"C1214472977-ASF","S1A RAW":"C1214470561-ASF","WV01_Pan_L1B":"C2497387766-CSDA","WV02_Pan_L1B":"C2497398128-CSDA",
 "WV02_MSI_L1B":"C2497404794-CSDA","GE01_Pan_L1B":"C2497510652-CSDA","QB02_Pan_L1B":"C2497480059-CSDA","IKONOS_Pan_L1B":"C2497468825-CSDA"}
def cmr_hits(cid=None,short=None,bb=BBOX,t=T):
    p={"bounding_box":bb,"temporal":t,"page_size":1}; p.update({"collection_concept_id":cid} if cid else {"short_name":short})
    return int(requests.get(CMR+"/granules.json",params=p,timeout=120).headers["CMR-Hits"])
def landsat_hits(bb=(100,-26.5,102.5,-25),dt="2014-03-08T00:00:00Z/2014-04-30T23:59:59Z"):
    j=requests.post("https://landsatlook.usgs.gov/stac-server/search",json={"bbox":list(bb),"datetime":dt,"collections":["landsat-c2l1"],"limit":200},timeout=120).json()
    return j.get("numberMatched",len(j.get("features",[])))
def cdse_hits(coll,t0="2014-03-08T00:00:00.000Z",t1="2014-06-01T00:00:00.000Z"):
    f=f"Collection/Name eq '{coll}' and OData.CSC.Intersects(area=geography'SRID=4326;{POLY}') and ContentDate/Start gt {t0} and ContentDate/Start lt {t1}"
    return len(requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",params={"$filter":f,"$top":"200"},timeout=120).json()["value"])
if __name__=="__main__":
    out={k:cmr_hits(v) for k,v in CMR_COLL.items()}; out["VNP02IMG"]=cmr_hits(short="VNP02IMG")
    out["Landsat c2l1"]=landsat_hits(); out["Landsat c2l1 Perth control"]=landsat_hits((115,-33,117,-31))
    out["CDSE SENTINEL-1"]=cdse_hits("SENTINEL-1"); print(json.dumps(out,indent=1))
