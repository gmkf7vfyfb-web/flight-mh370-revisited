
recs=[]
for daz in (-1.0,-0.5,0.0,0.5,1.0):
    line=Gd.Line(H01W[0],H01W[1],AZ+daz)
    for s in np.arange(R7-60,R7+250.01,1.0):
        p=line.Position(s*1e3); recs.append((daz,s-R7,p['lat2'],p['lon2']))
strip=pd.DataFrame(recs,columns=['dAz_deg','range_minus_R7_km','lat','lon'])
d,src,da,dg,t=depth(strip.lat.values,strip.lon.values)
strip['depth_m']=np.round(d,1); strip['source']=src; strip['gebco_tid']=t
os.makedirs('out',exist_ok=True); strip.to_csv('out/seabed_depth_bearing_strip.csv',index=False)
site_df.to_csv('out/seabed_depth_sites.csv',index=False)
g=strip.groupby('dAz_deg').depth_m.describe(percentiles=[.05,.5,.95]); print(g.round(0))
print('AusSeabed share by line', strip.groupby('dAz_deg').source.apply(lambda s:(s=='AusSeabed150').mean()).round(3).to_dict())
c=strip[strip.dAz_deg==0]
for lo_,hi_ in [(-60,0),(0,50),(50,100),(100,150),(150,200),(200,250)]:
    q=c[(c.range_minus_R7_km>=lo_)&(c.range_minus_R7_km<hi_)]
    print(lo_,hi_,q.depth_m.min(),q.depth_m.median(),q.depth_m.max(),(q.source=='AusSeabed150').mean().round(2))
