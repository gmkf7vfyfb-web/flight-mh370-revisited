
import importlib, sys, gsw
sys.path.insert(0,'.'); import settle_mc as sm; importlib.reload(sm)
ia=np.where((glat>=-32)&(glat<=-19))[0]; io=np.where((glon>=94)&(glon<=108))[0]
sub=np.asarray(Q[:, ia[0]:ia[-1]+1, io[0]:io[-1]+1])   # t,lat,lon,var,z
Ug,nv=sm.hold_deepest(sub[:,:,:,0,:]); Vg,_=sm.hold_deepest(sub[:,:,:,1,:])
slat=glat[ia]; slon=glon[io]
deepest=np.where(nv[1]>0, gz[np.maximum(nv[1]-1,0)], 0.0)     # deepest valid level depth per cell (day 2)
def mb_glorys(la,lo):
    i=np.clip(np.rint(np.interp(la,slat,np.arange(len(slat)))).astype(int),0,len(slat)-1); j=np.clip(np.rint(np.interp(lo,slon,np.arange(len(slon)))).astype(int),0,len(slon)-1)
    return deepest[i,j]
# density profile: TEOS-10 at the cell nearest the crossing, 8 March daily mean
ci=np.argmin(abs(slat-CX[0])); cj=np.argmin(abs(slon-CX[1]))
th=sub[1,ci,cj,2,:]; SP=sub[1,ci,cj,3,:]; ok=np.isfinite(th)
p_=gsw.p_from_z(-gz[ok],CX[0]); SA=gsw.SA_from_SP(SP[ok],p_,CX[1],CX[0]); CT=gsw.CT_from_pt(SA,th[ok]); rh=gsw.rho(SA,CT,p_)
# extend below deepest level by holding T,S and raising pressure
zext=np.append(gz[ok],[5000,6000,7000]); pe=gsw.p_from_z(-zext,CX[0]); rhe=np.append(rh, gsw.rho(np.full(3,SA[-1]),np.full(3,CT[-1]),pe[-3:]))
glorys=sm.Ocean('GLORYS12V1 daily (8 Mar 2014 column)',slat,slon,gt,gz,Ug,Vg,zext,rhe,mb_glorys)
wind=sm.Wind()
print(sub.shape, 'rho surface/4000m', rhe[0], np.interp(4000,zext,rhe), 'model bottom at HX', mb_glorys(np.array([HX[0]]),np.array([HX[1]])), 'wind', wind.W.shape)
u,v=glorys.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([0.5])); print('surface uv at HX 00:30',u,v)
u,v=glorys.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([3000.])); print('3000 m uv',u,v)
print(wind.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.])))
