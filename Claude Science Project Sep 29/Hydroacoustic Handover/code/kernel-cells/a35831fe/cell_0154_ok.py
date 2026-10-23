from pyproj import Geod
from scipy import stats
GW=Geod(ellps='WGS84')
nT0=1394236800
def hms_u(s): h,m,x=map(float,s.split(':')); return nT0+h*3600+m*60+x
H1=(-34.890303,114.142637); P74=(-38.536967,141.247567)
tH=hms_u('00:49:58'); t74=hms_u('01:15:51'); BRG=260.41
C0,SDC=1.482,0.006; SP1=10.0; SP2=np.hypot(10.0,2.0)
lat=S['lat']; lon=S['lon']; tu=S['t_unix']; w0=S['w_D0']
m=(w0>0)&(lat<-28)&(lat>-42)&(lon>84)&(lon<100)
la,lo,ti,wi=lat[m],lon[m],tu[m],w0[m]
az1,_,d1=GW.inv(np.full_like(lo,H1[1]),np.full_like(la,H1[0]),lo,la); d1/=1000
_,_,d2=GW.inv(np.full_like(lo,P74[1]),np.full_like(la,P74[0]),lo,la); d2/=1000
az1=np.mod(az1,360)
def wrap(x): return (x+180)%360-180
def L_bear(model):
    e=wrap(az1-BRG)
    if model=='t3': return stats.t.pdf(e,3,scale=3.3/np.sqrt(3))
    return stats.norm.pdf(e,scale=model)
def L_time_joint():
    r1=tH-ti-d1/C0; r2=t74-ti-d2/C0
    k=SDC/C0**2; a=SP1**2+(k*d1)**2; b=SP2**2+(k*d2)**2; c_=(k*d1)*(k*d2)
    det=a*b-c_**2; q=(b*r1**2-2*c_*r1*r2+a*r2**2)/det
    return np.exp(-0.5*q)/(2*np.pi*np.sqrt(det))
Lt=L_time_joint()
print('n',m.sum(),'w share in box',wi.sum()/w0.sum())
for mdl in ['t3',0.4,1.0]:
    W=wi*Lt*L_bear(mdl); W/=W.sum()
    mla=np.sum(W*la); mlo=np.sum(W*lo); ess=1/np.sum(W**2)
    print(mdl, f'mean {mla:.3f} {mlo:.3f}  ESS {ess:.0f}  impact t mean', fmt(np.sum(W*ti)-nT0)[:8])