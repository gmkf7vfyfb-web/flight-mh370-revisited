import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"); sys.path.insert(0, "/Users/pete/Downloads/mh370-exchange/hydroacoustics/session-staging-2026-10-12/g18")
import air9_tl_validation as A, kraken_tl as K, paths
SITES={"A2":(-32.8525,47.7357),"A4":(-30.87043,56.31747),"A5":(-28.73517,63.40160)}
RX={"H01W":(-34.892899,114.153900,1063.0),"H08S":(-7.639380,72.483828,1376.0),"H08N":(-6.337533,71.002077,1224.3)}
BANDS=[5.0,6.3,8.0,10.0,12.5,16.0,20.0,25.0,31.5,40.0,50.0,63.0]; SD=[610.0,915.0]; work="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro/g18"; rows=[]
for site,(la,lo) in SITES.items():
    for st,(rla,rlo,rd) in RX.items():
        name=f"{site}_{st}"; L,sh=paths.build(name,(la,lo),(rla,rlo),"95A4",5,f"{work}/paths")
        b=pd.read_csv(f"{work}/paths/bathy_{name}.csv"); s=pd.read_csv(f"{work}/paths/ssp_{name}.csv"); rp,pr=A.build_profiles(b,s); t0=time.time()
        for fc in BANDS:
            tag=f"f{fc:g}".replace(".","p")
            try:
                K.tl_path(f"{work}/k/{name}",tag,fc,pr,rp,np.array([rp[-1]]),SD,[rd],A.BOTTOMS["hard"],"/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/at",fg=A.FG)
                r=K.read_shd(f"{work}/k/{name}/{tag}.shd"); x=r["rr_m"]/1000/6371.0; sph=10*np.log10(x/np.sin(x))
                for js,zs in enumerate(r["sz"]): rows.append(dict(site=site,station=st,fc_hz=fc,src_depth_m=float(zs),range_km=L,shallowest_m=-sh,tl_db=float(-20*np.log10(abs(r["p"][0,js,0,-1]))+sph[-1])))
            except Exception as e:
                rows.append(dict(site=site,station=st,fc_hz=fc,src_depth_m=np.nan,range_km=L,shallowest_m=-sh,tl_db=np.nan,error=str(e)[:150]))
            for p in __import__("pathlib").Path(f"{work}/k/{name}").glob(f"{tag}.*"):
                if p.suffix in (".shd",".mod"): p.unlink()
        print(name,round(L),"km shallowest",-sh,round(time.time()-t0),"s",flush=True)
        pd.DataFrame(rows).to_csv(f"{work}/g18_tl.csv",index=False)
