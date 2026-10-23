import json, numpy as np
from shapely.geometry import shape, LineString
gj = json.load(open("/tmp/ne_land.geojson"))
land = [shape(f["geometry"]) for f in gj["features"]]
RX = {"Portland 3274": (-38.5370, 141.2476), "Perth Canyon 3376": (-31.8422, 115.0137),
      "Scott Reef 3250": (-15.4834, 121.2510), "H01W Cape Leeuwin": (-34.8929, 114.1539),
      "H08S Diego Garcia S": (-7.6453, 72.4744)}
def gc(lat1, lon1, lat2, lon2, n=400):
    p1,l1,p2,l2 = map(np.radians,(lat1,lon1,lat2,lon2))
    d = 2*np.arcsin(np.sqrt(np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin((l2-l1)/2)**2))
    f = np.linspace(0,1,n); A=np.sin((1-f)*d)/np.sin(d); B=np.sin(f*d)/np.sin(d)
    x=A*np.cos(p1)*np.cos(l1)+B*np.cos(p2)*np.cos(l2); y=A*np.cos(p1)*np.sin(l1)+B*np.cos(p2)*np.sin(l2)
    z=A*np.sin(p1)+B*np.sin(p2)
    return np.degrees(np.arctan2(z,np.hypot(x,y))), np.degrees(np.arctan2(y,x))
# 7th arc approximation from run I impacts: fit longitude as a function of latitude
la = S["baseline"][:,ci["latitude_deg"]]; lo = S["baseline"][:,ci["longitude_deg"]]
cf = np.polyfit(la, lo, 2)
print("arc fit lon(lat) coeffs:", np.round(cf,5), "| impact lat range", round(la.min(),2), round(la.max(),2))
rows=[]
for lat in np.arange(-40, -17.9, 0.5):
    lon = float(np.polyval(cf, lat))
    r = {"lat": lat, "lon": round(lon,2)}
    for nm,(rla,rlo) in RX.items():
        py,px = gc(lat, lon, rla, rlo)
        ls = LineString(np.column_stack([px,py]))
        r[nm] = "blocked" if any(ls.intersects(p) for p in land) else "clear"
    rows.append(r)
import pandas as pd
df = pd.DataFrame(rows)
for nm in RX:
    bl = df[df[nm]=="blocked"]["lat"]
    print(f"{nm:22s} blocked at latitudes: {('none' if bl.empty else f'{bl.max():.1f} to {bl.min():.1f} deg')}")
print(df.to_string(index=False))
