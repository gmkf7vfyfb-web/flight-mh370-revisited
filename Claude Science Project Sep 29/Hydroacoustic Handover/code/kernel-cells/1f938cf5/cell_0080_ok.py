
hla=H['lat'][1162:1201]; hlo=H['lon'][3500:3533]; hz=H['depth']; htt=T0+np.array([0.0,3*3600.0])
Uh,nvh=sm.hold_deepest(np.transpose(HY['water_u'],(0,2,3,1))); Vh,_=sm.hold_deepest(np.transpose(HY['water_v'],(0,2,3,1)))
deep_h=np.where(nvh[0]>0, hz[np.maximum(nvh[0]-1,0)],0.0)
def mb_h(la,lo):
    i=np.clip(np.rint(np.interp(la,hla,np.arange(len(hla)))).astype(int),0,len(hla)-1); j=np.clip(np.rint(np.interp(lo,hlo,np.arange(len(hlo)))).astype(int),0,len(hlo)-1)
    return deep_h[i,j]
ci=np.argmin(abs(hla-CX[0])); cj=np.argmin(abs(hlo-CX[1]))
t_=HY['water_temp'][0,:,ci,cj]; S_=HY['salinity'][0,:,ci,cj]; ok=np.isfinite(t_)
p_=gsw.p_from_z(-hz[ok],CX[0]); SA=gsw.SA_from_SP(S_[ok],p_,CX[1],CX[0]); rh=gsw.rho(SA,gsw.CT_from_t(SA,t_[ok],p_),p_)
zext_h=np.append(hz[ok],[5000.,6000.,7000.]); pe=gsw.p_from_z(-zext_h[-3:],CX[0])
CTd=gsw.CT_from_t(SA[-1],t_[ok][-1],p_[-1]); rhe_h=np.append(rh,gsw.rho(np.full(3,SA[-1]),np.full(3,CTd),pe))
hycom=sm.Ocean('HYCOM GOFS 3.1 expt 53.X (8 Mar 2014 00Z, 03Z)',hla,hlo,htt,hz,Uh,Vh,zext_h,rhe_h,mb_h)
print('HYCOM model bottom at HX',mb_h(np.array([HX[0]]),np.array([HX[1]])),'rho 4000',np.interp(4000,zext_h,rhe_h),'vs GLORYS',np.interp(4000,zext,rhe))
print('surface uv HX', hycom.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([0.0])), 'GLORYS', glorys.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([0.5])))
for zz in (500,1500,3000,4300):
    print(zz,'HYCOM',np.round(np.ravel(hycom.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([zz]))),3),'GLORYS',np.round(np.ravel(glorys.uv(np.array([HX[0]]),np.array([HX[1]]),np.array([T0+1800.]),np.array([zz]))),3))
for cls in CLASSES:
    o=sm.settle(np.full(20000,HX[0]),np.full(20000,HX[1]),T0+rowsH2.t_impact_s.values,rowsH2.vh.values,tr2,fam2,cls,hycom,wind,np.random.default_rng(7))
    dx,dy=sm.offsets_km(HX[0],HX[1],o['lat'],o['lon']); D=np.hypot(dx,dy)
    sens_o.append(dict(ocean='HYCOM GOFS 3.1 (53.X)',cls=cls,p50=np.nanpercentile(D,50),p90=np.nanpercentile(D,90),p99=np.nanpercentile(D,99),mean_dx=np.nanmean(dx),mean_dy=np.nanmean(dy)))
    RES.setdefault('at_haixun_hycom',{})[cls]=dict(dx=dx,dy=dy,D=D,fam=fam2,depth=o['depth'],floated=o['floated'])
SO=pd.DataFrame(sens_o); print(SO[SO.ocean.isin(['GLORYS12V1 baseline','HYCOM GOFS 3.1 (53.X)'])].round(3).to_string())
