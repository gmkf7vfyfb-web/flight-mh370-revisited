def gran_all(cid,bb,temporal):
    out=[];page=1
    while True:
        r=requests.get(CMR+"/granules.json",params={"bounding_box":bb,"temporal":temporal,"page_size":2000,"page_num":page,"collection_concept_id":cid},timeout=120)
        e=r.json()["feed"]["entry"]; out+=e
        if len(e)<2000: break
        page+=1
    return out
import numpy as np
recs=[]
for s,i in sel:
    for e in gran_all(i,"85,-47,110,-18",T):
        pts=None
        if "polygons" in e:
            c=list(map(float,e["polygons"][0][0].split())); lat=c[0::2]; lon=c[1::2]; pts=(np.mean(lat),np.mean(lon),min(lat),max(lat),min(lon),max(lon))
        elif "boxes" in e:
            s_,w,n_,ee=map(float,e["boxes"][0].split()); pts=((s_+n_)/2,(w+ee)/2,s_,n_,w,ee)
        recs.append(dict(coll=s,id=e.get("producer_granule_id") or e["title"],t=e["time_start"],clat=pts[0],clon=pts[1],latmin=pts[2],latmax=pts[3],lonmin=pts[4],lonmax=pts[5],cloud=e.get("cloud_cover")))
import pandas as pd
df=pd.DataFrame(recs); df["date"]=df.t.str[:10]
print(len(df)); print(df.groupby(["coll","date"]).agg(n=("id","size"),clat=("clat","mean"),clon=("clon","mean"),latmin=("latmin","min"),latmax=("latmax","max"),lonmin=("lonmin","min"),lonmax=("lonmax","max")).round(2).to_string())