def gran(cid=None,short=None,page=2000,temporal=tq):
    p={"bounding_box":bbox,"temporal":temporal,"page_size":page}
    if cid: p["collection_concept_id"]=cid
    if short: p["short_name"]=short
    r=requests.get(CMR+"/granules.json",params=p,timeout=120)
    return int(r.headers.get("CMR-Hits",-1)), r.json()["feed"]["entry"] if r.ok else r.text[:200]
targets={"Landsat L1 C2 (USGS)":"C3442493460-USGS_EROS","L7 ETM SLC-off (LTA)":"C1220567903-USGS_LTA","HLS L30":"C2021957657-LPCLOUD",
"ASTER L1T":"C3306888411-LPCLOUD","EO-1 ALI":"C1220566654-USGS_LTA","EO-1 Hyperion":"C1220567951-USGS_LTA",
"MODIS Terra 250m (MOD02QKM 6.1)":"C1378579425-LAADS","MODIS Aqua 250m (MYD02QKM 6.1)":"C1379759127-LAADS",
"S1A SLC (ASF)":"C1214470488-ASF","S1A GRD high (ASF)":"C1214470533-ASF","S1A OCN (ASF)":"C1214472977-ASF","S1A RAW (ASF)":"C1214470561-ASF"}
gr={}
for k,c in targets.items():
    try: n,e=gran(c); gr[k]=e; print(k,n)
    except Exception as ex: print(k,"ERR",str(ex)[:120])
for s in ["VNP02IMG","VNP03IMG"]:
    try: n,e=gran(short=s); gr["VIIRS "+s]=e; print(s,n)
    except Exception as ex: print(s,"ERR",str(ex)[:100])