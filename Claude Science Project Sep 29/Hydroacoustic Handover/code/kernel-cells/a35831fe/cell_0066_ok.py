pts=G.npts(100.93,-26.34,rx['3275'][1],rx['3275'][0],200)
for lo_,la_ in pts[::20]: print(round(lo_,1),round(la_,2))
# Kadri 00:40:34 vs 3275 timing via geodesic (ignoring land)
import json
gm=json.load(open('/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json')); print({k:gm[k] for k in list(gm)[:12]})