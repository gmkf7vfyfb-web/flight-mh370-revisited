def val(c,lat,lon):
    i=int(np.floor((lat-c['s'])/c['st'])); j=int(np.floor((lon-c['w'])/c['st']))
    if 0<=i<c['R'] and 0<=j<c['C']: return c['a'][i,j]
    return 0.0
oi=cov['ocean-infinity-2018']
pts={'crossing':(-25.732,101.369),'haixun':(-25.975,101.461),'kadri1586':(-25.764,101.408)}
for k,(la,lo) in pts.items(): print(k, val(oi,la,lo))
# per-latitude row extents of OI coverage north of 28 S
for lat in np.arange(-28.0,-24.7,0.25):
    i=int(np.floor((lat-oi['s'])/oi['st'])); row=oi['a'][i]; jj=np.nonzero(row>0)[0]
    if jj.size: print(round(lat,2), 'lon %.2f-%.2f'%(oi['w']+jj.min()*0.01, oi['w']+(jj.max()+1)*0.01), 'ncells',jj.size, 'mean',row[jj].mean().round(2))