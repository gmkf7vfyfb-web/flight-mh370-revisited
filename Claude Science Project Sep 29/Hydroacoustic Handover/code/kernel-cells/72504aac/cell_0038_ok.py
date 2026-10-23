
gj=json.load(open('/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json')); print({k:gj[k] for k in gj if not isinstance(gj[k],(list,dict))})
el=np.memmap('/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026_elevation.i16',dtype=np.int16,mode='r',shape=(gj['nlat'],gj['nlon']))
def gidx(lat,lon): return int(round((lat-gj['lat0'])/gj['step_deg'])), int(round((lon-gj['lon0'])/gj['step_deg']))
for la,lo in [(-(31+50.5/60),115+0.8/60),(-31.95,115.86),(-33.5,94.5)]:
    i,j=gidx(la,lo); print(la,lo,i,j, el[i,j] if 0<=i<gj['nlat'] and 0<=j<gj['nlon'] else None)
