import numpy as np, pandas as pd, io, subprocess
st = subprocess.run(['git','show','FETCH_HEAD:Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/stations.csv'],cwd='repo',capture_output=True,text=True).stdout
S = pd.read_csv(io.StringIO(st)); print(S.iloc[:, :4].to_string())
def gc(lat1,lon1,lat2,lon2,R=6371.0):
    p1,p2,dl=map(np.radians,(lat1,lat2,lon2-lon1)); 
    return R*np.arccos(np.clip(np.sin(p1)*np.sin(p2)+np.cos(p1)*np.cos(p2)*np.cos(dl),-1,1))
h = S[S.iloc[:,0].astype(str).str.contains('H01W')].iloc[0]
latc=[c for c in S.columns if 'lat' in c.lower()][0]; lonc=[c for c in S.columns if 'lon' in c.lower()][0]
arc = {'38S 88.45E':(-38,88.45),'37.23S 89.58E':(-37.23,89.58),'34S 94.23E':(-34,94.23),'30S 98.31E':(-30,98.31),'25.8S 101.4E':(-25.8,101.4),'20S 103.5E':(-20,103.5)}
for k,(la,lo) in arc.items():
    d=gc(h[latc],h[lonc],la,lo); print(f"{k}: {d:.0f} km, delay {d/1.48/60:.1f} min at 1.48 km/s")
# poster panel (a) boxes, minutes after 00:27 (read from image)
boxes=[(1.2,2.7),(3.4,4.9),(5.5,7.0),(8.4,9.9)]
for a,b in boxes:
    print(f"box 00:{27+int(a)}:{int((a%1)*60):02d}-00:{27+int(b)}:{int((b%1)*60):02d} -> impact if 1,684 km: 00:{27+int(a)-19}:xx .. ; needs range <= {(27+b-19.5)*60*1.48:.0f} km for an impact at 00:19:30")