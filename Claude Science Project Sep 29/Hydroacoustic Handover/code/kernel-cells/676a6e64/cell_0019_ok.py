import numpy as np
def gc(lat1,lon1,lat2,lon2,R=6371.0):
    p1,p2,dl=map(np.radians,(lat1,lat2,lon2-lon1))
    return R*np.arccos(np.clip(np.sin(p1)*np.sin(p2)+np.cos(p1)*np.cos(p2)*np.cos(dl),-1,1))
lat,lon=-34.892899,114.1539
arc = {'38S 88.45E':(-38,88.45),'37.23S 89.58E':(-37.23,89.58),'34S 94.23E':(-34,94.23),'30S 98.31E':(-30,98.31),'25.8S 101.4E':(-25.8,101.4),'20S 103.5E':(-20,103.5)}
for k,(la,lo) in arc.items():
    d=gc(lat,lon,la,lo); print(f"{k}: {d:.0f} km, delay {d/1.48/60:.1f} min")
boxes=[(1.2,2.7),(3.4,4.9),(5.5,7.0),(8.4,9.9)]
for a,b in boxes:
    t0=27+a; t1=27+b
    print(f"box 00:{int(t0):02d}:{int(round((t0%1)*60)):02d}-00:{int(t1):02d}:{int(round((t1%1)*60)):02d} -> max range for impact at/after 00:19:30: {(t1-19.5)*60*1.48:.0f} km")