
tl=pd.read_csv(X+'/hydroacoustics/run-j-tl-grid/tables/tl_grid.csv.gz')
src=tl[tl.offset_nm==0][['src_lat','src_lon']].drop_duplicates().sort_values('src_lat')
print(len(src), src.src_lat.min(), src.src_lat.max(), np.diff(src.src_lat.values)[:3])
from scipy.interpolate import interp1d
f=interp1d(src.src_lat.values, src.src_lon.values, kind='cubic')
tlLat=np.linspace(src.src_lat.min(), src.src_lat.max(), 40001); tlLon=f(tlLat)
def locus2(lag, ra='H01W', rb='H08S', lats=tlLat, lons=tlLon, win=(-41,-20)):
    la,lo=rx[ra]; _,_,da=G84.inv(np.full_like(lats,lo),np.full_like(lats,la),lons,lats)
    la,lo=rx[rb]; _,_,db=G84.inv(np.full_like(lats,lo),np.full_like(lats,la),lons,lats)
    L=(db-da)/1000/1.482; ok=(lats>win[0])&(lats<win[1]); s=np.sign(L-lag)
    idx=np.nonzero(ok[:-1]&ok[1:]&(s[:-1]!=s[1:]))[0]
    return [(round(lats[i],3),round(lons[i],3),round(da[i]/1000,1)) for i in idx]
print('G', locus2(1245)); print('E', locus2(lagE)); print('F', locus2(lagF))
# compare arcs at -33.56
print(np.interp(-33.565, arcLat[::-1] if arcLat[0]>arcLat[-1] else arcLat, arcLon[::-1] if arcLat[0]>arcLat[-1] else arcLon), f(-33.565))
