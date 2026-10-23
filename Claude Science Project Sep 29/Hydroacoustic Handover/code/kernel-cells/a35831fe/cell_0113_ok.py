import subprocess, io
def gshow(p): return subprocess.run(['git','-C','main','show','HEAD:'+p],capture_output=True,text=True).stdout
plei=pd.read_csv(io.StringIO(gshow('ISO Sept 28 Status/inputs/recovered-v01/.sources/pleiades-bran2016-forward-inversion/data/pleiades-rating5-objects.csv')))
cosmo=pd.read_csv(io.StringIO(gshow('Claude Science Project Sep 29/engine/hypotheses/pleiades/data/cosmo-contacts.csv')))
print(len(plei), cosmo.shape)
# HPD helper
def hpd_level(Mx,q):
    v=np.sort(Mx.ravel())[::-1]; c_=np.cumsum(v)/v.sum(); return v[np.searchsorted(c_,q)]
# coast from GEBCO coarse
cl_lat=np.arange(-46,8,0.05); cl_lon=np.arange(70,125,0.05)
ii=((cl_lat-gm['lat0'])/gm['step_deg']).round().astype(int); jj=((cl_lon-gm['lon0'])/gm['step_deg']).round().astype(int)
ok_i=(ii>=0)&(ii<gm['nlat']); ok_j=(jj>=0)&(jj<gm['nlon'])
ELV=np.full((len(cl_lat),len(cl_lon)),-4000,dtype=np.int16)
ELV[np.ix_(ok_i,ok_j)]=el[np.ix_(ii[ok_i],jj[ok_j])]
print(ELV.shape, (ELV>0).mean(), gm['lat0']+gm['nlat']*gm['step_deg'])