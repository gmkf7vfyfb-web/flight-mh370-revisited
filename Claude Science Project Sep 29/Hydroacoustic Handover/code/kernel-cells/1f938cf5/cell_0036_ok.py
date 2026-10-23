
from pyproj import Geod
gw=Geod(ellps='WGS84')
lat=L.latitude_deg.values.astype(float); lon=L.longitude_deg.values.astype(float); n=len(L)
az1,_,s=gw.inv(np.full(n,H01W[1]),np.full(n,H01W[0]),lon,lat)
L['rng_km']=s/1e3; L['az']=az1%360
L['dCX']=gw.inv(np.full(n,CX[1]),np.full(n,CX[0]),lon,lat)[2]/1e3
L['dHX']=gw.inv(np.full(n,HX[1]),np.full(n,HX[0]),lon,lat)[2]/1e3
L['in_strip']=(L.rng_km>=R7-60)&(L.rng_km<=R7+250)&(abs(L.az-AZ)<=1.0)
for r_ in (50,100,200,400):
    L[f'CX{r_}']=L.dCX<=r_; L[f'HX{r_}']=L.dHX<=r_
print(L[['in_strip','CX50','CX100','CX200','HX50','HX100','HX200']].sum().to_dict())
print(L.groupby('stratum')[['in_strip','CX50','HX50','CX100']].sum())
print('min dHX',L.dHX.min(),'min dCX',L.dCX.min(), 'n within 10 km HX', (L.dHX<10).sum())
