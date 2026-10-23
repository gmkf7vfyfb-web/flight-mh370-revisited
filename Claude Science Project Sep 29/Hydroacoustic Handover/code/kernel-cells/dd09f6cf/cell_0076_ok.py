from scipy.optimize import brentq
from scipy.ndimage import gaussian_filter
Cl=299792.458; GES=np.array([-2368.8,4881.1,-3342.0]); OFF=499962.0-4283.0; SAT=np.array([18178.3537,38050.8487,393.0782])
A_=6378.137; F_=1/298.257223563; E2=F_*(2-F_)
def ecef(lat,lon,h=0):
    la,lo=np.radians(lat),np.radians(lon); N=A_/np.sqrt(1-E2*np.sin(la)**2)
    return np.array([(N+h)*np.cos(la)*np.cos(lo),(N+h)*np.cos(la)*np.sin(lo),(N*(1-E2)+h)*np.sin(la)])
def bto(lat,lon): return 2*(np.linalg.norm(SAT-ecef(lat,lon))+np.linalg.norm(SAT-GES))/Cl*1e6-OFF
arc_lat=np.arange(-40,-15,0.05); arc_lon=np.array([brentq(lambda lo: bto(la,lo)-18400,80,120) for la in arc_lat])
print('arc at -25.732:',np.interp(-25.732,arc_lat,arc_lon), 'BTO at Haixun %.1f'%bto(-25.975,101.461))
def hpd_grid(df, ext=(99,104,-27.5,-23.0), st=0.02, sig=2.0):
    xe=np.arange(ext[0],ext[1]+st,st); ye=np.arange(ext[2],ext[3]+st,st)
    h,_,_=np.histogram2d(df.lon.values,df.lat.values,bins=[xe,ye],weights=df.w.values); h=gaussian_filter(h.T,sig)
    inside_mass=float(df.w[(df.lon>=ext[0])&(df.lon<=ext[1])&(df.lat>=ext[2])&(df.lat<=ext[3])].sum())
    v=np.sort(h.ravel())[::-1]; c=np.cumsum(v)/v.sum(); lev=[v[np.searchsorted(c,q)] for q in (0.99,0.9,0.5)]
    return xe,ye,h,lev,inside_mass
DF={ak:rows_weighted('D0',ak) for ak in ['Tcore','Ccore']}
for ak,df in DF.items():
    xe,ye,h,lev,im=hpd_grid(df); print(ak,'mass inside map window %.3f'%im)