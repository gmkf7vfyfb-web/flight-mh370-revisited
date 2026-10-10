import json, pathlib, numpy as np, hashlib
from scipy.special import gammaln
E=pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/83c5d472-a2a6-4ff0-9602-ceefbdadb1ad/repo/Claude Science Project Sep 29/engine/runs")
G=pathlib.Path("/Users/pete/Downloads/mh370-ocean-data/gebco/grid")
gm=json.load(open(G/"gebco_2026.json")); Z=np.memmap(G/gm["elevation_file"],dtype="<i2",mode="r",shape=(gm["nlat"],gm["nlon"]))
def depth(lat,lon):
    j=np.rint((lat-gm["lat0"])/gm["step_deg"]).astype(int); i=np.rint((lon-gm["lon0"])/gm["step_deg"]).astype(int)
    ok=(i>=0)&(j>=0)&(i<gm["nlon"])&(j<gm["nlat"]); d=np.full(lat.shape,np.nan); d[ok]=-Z[j[ok],i[ok]].astype(float); return d
OPTS=["none","r600/inflated","r1200/inflated"]
def wq(x,w,qs):
    o=np.argsort(x); x,w=x[o],w[o]; c=np.cumsum(w)/w.sum(); return [float(x[np.searchsorted(c,q)]) for q in qs]
out={"seeds":[],"options":{}}
acc={}
for k in (1,2,3,4):
    run=E/f"eof-289-full-s{k}"; sd=run/"bto-bfo"/f"seed-{k}"
    meta=json.loads((run/"run.json").read_text()); cols={c:i for i,c in enumerate(meta["impact_columns"])}
    logon=meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    X=np.load(sd/"impacts.npy",mmap_mode="r"); g=lambda c: np.asarray(X[:,cols[c]],float)
    w=g("weight"); lat=g("latitude_deg"); lon=g("longitude_deg"); fam=g("family") if "family" in cols else None
    dc=None
    d=depth(lat,lon)
    lag=logon["logon_unix_s"]-g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore",invalid="ignore"):
        lfe=(logon["lag_shape"]-1)*np.log(lag)-lag/logon["lag_scale_s"]-logon["lag_shape"]*np.log(logon["lag_scale_s"])-gammaln(logon["lag_shape"])
    lfe=np.where(np.isfinite(lag)&(lag>0),lfe,-np.inf)
    def find(o,path=""):
        if isinstance(o,dict):
            for kk,v in o.items(): yield from find(v,path+"/"+kk)
        elif isinstance(o,(int,float)) and abs(o-289.7)<1e-6: yield path
    out["seeds"].append({"seed":k,"run":str(run),"code_revision":meta.get("code_revision"),"config_paths":meta.get("config_paths"),"source_run":meta.get("source_run"),"keys_equal_289.7":list(find(meta["config"]))})
    for o in OPTS:
        if "loglik:"+o not in cols: continue
        base=g("loglik:"+o)
        for cause,extra in (("other",0.0),("fuel-exhaustion",lfe)):
            ll=np.where(np.isfinite(base),base,-np.inf)+extra; p=w*np.exp(ll-ll[np.isfinite(ll)].max()); p/=p.sum()
            key=f"{o.replace('/','_')}__{cause}"
            a=acc.setdefault(key,{"d":[],"lat":[],"lon":[],"p":[],"dc":[]})
            m=np.isfinite(d)&(p>0)
            a["d"].append(d[m]); a["lat"].append(lat[m]); a["lon"].append(lon[m]); a["p"].append(p[m]/4.0)
            if dc is not None: a["dc"].append(dc[m])
    print("seed",k,"done",flush=True)
for key,a in acc.items():
    d=np.concatenate(a["d"]); la=np.concatenate(a["lat"]); lo=np.concatenate(a["lon"]); p=np.concatenate(a["p"])
    r={"depth_q05_10_25_50_75_90_95":wq(d,p,[.05,.1,.25,.5,.75,.9,.95]),"shallow_lt_200m_mass":float(p[d<200].sum()/p.sum()),"land_mass":float(p[d<=0].sum()/p.sum()),
       "lat_q10_50_90":wq(la,p,[.1,.5,.9])}
    if a["dc"]:
        dc=np.concatenate(a["dc"]); r["debris_class_mass"]=[float(p[dc==c].sum()/p.sum()) for c in (0,1,2)]
    # representative points: highest-mass 0.25 deg cell within 0.125 deg of each latitude quantile, plus mode cell
    ci=np.floor(la/0.25).astype(int); cj=np.floor(lo/0.25).astype(int)
    keys=ci*100000+cj; u,inv=np.unique(keys,return_inverse=True); cw=np.bincount(inv,weights=p)
    clat=(u//100000+0.5)*0.25; clon=(u%100000+0.5)*0.25
    # fix negative floor division for lon positive, lat negative
    clat=(np.floor_divide(u+50000,100000)+0.5)*0.25
    clon=((u+50000)%100000-50000+0.5)*0.25
    pts=[]
    for q in r["lat_q10_50_90"]:
        b=np.abs(clat-q)<=0.125+1e-9; i=np.where(b)[0][np.argmax(cw[b])]; pts.append([float(clat[i]),float(clon[i])])
    i=np.argmax(cw); r["mode_cell"]=[float(clat[i]),float(clon[i])]; r["points_lat_q10_50_90"]=pts
    out["options"][key]=r
json.dump(out,open("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/770a0941-603a-4490-929c-9fdb91cd5434/depth289.json","w"),indent=1)
