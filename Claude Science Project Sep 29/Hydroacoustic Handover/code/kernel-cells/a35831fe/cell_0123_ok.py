PS=EX+'pleiades/run-j/surfaces/'
mt={}
for line in open(PS+'joint-surface-rho0.25-gcrel.toml').read().splitlines():
    k_,v_=line.split(' = ',1); mt[k_]=v_
J=np.fromfile(PS+'joint-surface-rho0.25-gcrel.f32','<f4').reshape(2,int(mt['nlat']),int(mt['nlon'])).astype(float)
J=np.where(np.isfinite(J),J,-np.inf); lnL=np.logaddexp(J[0],J[1])-np.log(2.0)
fo_=PM['post'].astype(float)   # flight-only impact cell mass (pre = post per README)
w_=fo_*np.exp(lnL-np.nanmax(lnL[fo_>0])); w_[~np.isfinite(w_)]=0; condH=w_/w_.sum()
LA,LO=np.meshgrid(plat,plon,indexing='ij')
def wmean(Wm): return (Wm*LA).sum(), (Wm*LO).sum()
print('flight-only mean', np.round(wmean(fo_/fo_.sum()),2), ' conditional-on-H mean', np.round(wmean(condH),2))
lvH=[hpd_level(gaussian_filter(condH,1.0)/gaussian_filter(condH,1.0).sum(),q) for q in (0.9,0.5)]
for nm_,Mx in [('flight-only',fo_/fo_.sum()),('cond H',condH)]:
    Ms=gaussian_filter(Mx,1.0); Ms/=Ms.sum(); l50=hpd_level(Ms,0.5); k_=Ms>=l50
    print(nm_, '50% HPD lat range', LA[k_].min(), LA[k_].max(), 'lon', LO[k_].min(), LO[k_].max(), 'area share', k_.mean())
# cross-check against composer core x Pleiades (seabed) product
mapP=MP3['D0|P'].astype(float).reshape(NY,NX); mapP/=mapP.sum(); YY,XX=np.meshgrid(yc,xc,indexing='ij')
print('composer D0|P seabed mean', round((mapP*YY).sum(),2), round((mapP*XX).sum(),2))