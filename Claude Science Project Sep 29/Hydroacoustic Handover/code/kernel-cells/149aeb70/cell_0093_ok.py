import numpy as np
from shapely.geometry import LineString
def blocked(lat, lon, rx):
    py,px = gc(lat, lon, *rx); ls = LineString(np.column_stack([px,py]))
    return any(ls.intersects(p) for p in land)
lo_, hi_ = -29.5, -28.0
for _ in range(40):
    mid = (lo_+hi_)/2
    if blocked(mid, float(np.polyval(cf, mid)), RX["Portland 3274"]): lo_ = mid
    else: hi_ = mid
print(f"Portland becomes land-blocked north of {hi_:.2f} deg S (arc longitude {float(np.polyval(cf,hi_)):.2f} E)")
r = host.artifacts(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", limit=300)
for a in r["artifacts"]:
    f=a["filename"].lower()
    if any(k in f for k in ("kadri","transient","bearing","candidate","table1")):
        print(a["filename"], "|", a.get("size_bytes"), "|", a["latest_version_id"])
