
from scipy.spatial import cKDTree
CORE=X+'/core/run-j/run-j-waypoints/bto-bfo'
def xyz(la,lo):
    la,lo=np.radians(la),np.radians(lo); return np.c_[np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)]
frac=550/600
ROUTES=[]; RINFO=[]; NEAR=[]; WTOT=0; W150TOT=0
for k in range(1,25):
    zz=np.load(f'work/seed-{k}.npz'); Wp,W150=zz['Wp'],zz['W150']; WTOT+=Wp.sum(); W150TOT+=W150.sum()
    h=np.load(f'{CORE}/seed-{k}/handoff-m0011/handoff.npy'); hl,ho=h[:,1],h[:,2]; npar=len(Wp)
    assert len(h)>=npar, (len(h),npar)
    r=np.load(f'{CORE}/seed-{k}/routes.npy').astype(float)
    p=r[:,36]+(r[:,37]-r[:,36])*frac
    t=cKDTree(xyz(hl[:npar],ho[:npar])); dn,jn=t.query(xyz(p[:,0],p[:,1]))
    nb=t.query_ball_point(xyz(p[:,0],p[:,1]), r=10/6371.0)
    f=np.empty(len(r)); m=np.empty(len(r)); nn=np.empty(len(r),int)
    for i,lst in enumerate(nb):
        lst=lst if len(lst) else [jn[i]]; s=Wp[lst].sum(); f[i]=W150[lst].sum()/s if s>0 else np.nan; m[i]=s/len(lst); nn[i]=len(lst)
    ROUTES.append(r); RINFO.append(pd.DataFrame(dict(seed=k,route=np.arange(len(r)),f150=f,parent_mass=m,n_match=nn,d_nearest_km=dn*6371.0,nearest_parent=jn)))
    sel=zz['d']<150
    NEAR.append(pd.DataFrame({c:zz[c][sel] for c in ['parent','w','lat','lon','d','t_impact_s','t_takeover_s','t_onset_s','t_realised_flameout_s','takeover_latitude_deg','takeover_longitude_deg','takeover_altitude_ft','family4_code','last_burst_latitude_deg','last_burst_longitude_deg','max_descent_rate_fpm']}).assign(seed=k, h_lat=lambda d: hl[d.parent.astype(int)], h_lon=lambda d: ho[d.parent.astype(int)]))
RI=pd.concat(RINFO,ignore_index=True); NR=pd.concat(NEAR,ignore_index=True); ROUTES=np.stack(ROUTES)
print(ROUTES.shape, len(NR), 'share within150 (waypoints, all seeds)', W150TOT/WTOT)
print(RI.describe().T[['mean','50%','min','max']])
print('routes with f150>=0.5:', (RI.f150>=0.5).sum(), ' weighted near share', np.nansum(RI.f150)/RI.f150.notna().sum())
