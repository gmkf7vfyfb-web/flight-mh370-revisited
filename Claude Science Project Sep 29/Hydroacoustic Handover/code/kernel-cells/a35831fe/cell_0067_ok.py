el=np.memmap('/Users/pete/Downloads/mh370-ocean-data/gebco/grid/'+gm['elevation_file'],dtype='<i2',mode='r',shape=(gm['nlat'],gm['nlon']))
def elev(lo_,la_):
    i=int(round((la_-gm['lat0'])/gm['step_deg'])); j=int(round((lo_-gm['lon0'])/gm['step_deg'])); return int(el[i,j])
def path_land(la1,lo1,la2,lo2,n=2000):
    p=G.npts(lo1,la1,lo2,la2,n); e=np.array([elev(a,b) for a,b in p]); return (e>0).sum(), e.max(), p[int(np.argmax(e))]
# sanity: a known land point Perth 31.95S 115.86E and ocean 35S 100E
print(elev(115.86,-31.95), elev(100,-35))
print('3275 from Kadri 00:40:34 locus:', path_land(-26.34,100.93,*rx['3275']))
print('3315 from same:', path_land(-26.34,100.93,*rx['3315']))
print('3275 from 37 S 90 E:', path_land(-37,90,*rx['3275']))
print('3274 from 36.7S 90.3E:', path_land(-36.74,90.29,*rx['3274']))
print('3275 from 33.5S 94.6E:', path_land(-33.53,94.55,*rx['3275']))