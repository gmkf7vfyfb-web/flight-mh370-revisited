
from datetime import datetime
h0=(datetime(2014,3,8,0)-datetime(2000,1,1)).total_seconds()/3600
it=np.where((H['time']>=h0-3)&(H['time']<=h0+15))[0]
ila=np.where((H['lat']>=-28.0)&(H['lat']<=-23.0))[0]; ilo=np.where((H['lon']>=98.5)&(H['lon']<=104.0))[0]
print(H['time'][it]-h0, ila[[0,-1]], ilo[[0,-1]], len(ila),len(ilo))
B="https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2014"
sl=f"[{it[0]}:{it[-1]}][0:39][{ila[0]}:{ila[-1]}][{ilo[0]}:{ilo[-1]}]"
with open('hycom/urls.txt','w') as f:
    for v in ['water_u','water_v','water_temp','salinity']: f.write(f"{v} {B}.ascii?{v}{sl}\n")
print(open('hycom/urls.txt').read()[:200])
