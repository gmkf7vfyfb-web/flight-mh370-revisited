latc=W.LOC['lat0']+(np.arange(ni)+0.5)*0.05; lonc=W.LOC['lon0']+(np.arange(nj)+0.5)*0.05
for d in (0,2,3,4):
    k=f'D{d} total q=0.333 (C2 silent)'
    for vn in ('T1.0','C1.0'):
        H,_=getmap('main',k,vn); l99=hpd_levels(H,(0.99,))[0]; ii,jj=np.nonzero(H>=l99)
        print(d,vn, latc[ii].min().round(2),latc[ii].max().round(2),lonc[jj].min().round(2),lonc[jj].max().round(2))