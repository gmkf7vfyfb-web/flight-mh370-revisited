
import os, json, datetime as dt, numpy as np
os.makedirs('jobsnap',exist_ok=True)
rel=json.load(open('L_releases.json'))
def ux(y,m,d,h=0): return dt.datetime(y,m,d,h,tzinfo=dt.timezone.utc).timestamp()
times=[ux(2014,3,15),ux(2014,3,22),ux(2014,3,29),ux(2014,4,3),ux(2014,4,4),ux(2014,4,4,12),ux(2014,4,5),ux(2014,4,5,12),ux(2014,4,6)]
def spec(rels,fn):
    s="releases = ["+", ".join(f"[{lo:.5f}, {la:.5f}, {t:.1f}]" for lo,la,t in rels)+"]\n"
    s+="times = ["+", ".join(f"{t:.1f}" for t in times)+"]\n"
    open(fn,'w').write(s)
spec([(r['lon'],r['lat'],r['unix']) for r in rel],'jobsnap/spec-L.toml')
# connectivity grid, single release time 00:35:00 UTC
tg=ux(2014,3,8)+35*60
lons=np.round(np.arange(96.0,106.5001,0.25),3); lats=np.round(np.arange(-31.0,-20.9999,0.25),3)
grid=[(lo,la,tg) for la in lats for lo in lons]
print(len(lons),len(lats),len(grid))
nch=int(np.ceil(len(grid)/250))
for i in range(nch): spec(grid[i*250:(i+1)*250],f'jobsnap/spec-G{i}.toml')
json.dump(dict(times=times,grid_lons=lons.tolist(),grid_lats=lats.tolist(),grid_t=tg,nchunks=nch,L=rel),open('jobsnap/meta.json','w'))
print(nch)
