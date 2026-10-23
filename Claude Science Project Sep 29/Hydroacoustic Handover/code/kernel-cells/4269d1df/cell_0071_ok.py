
def origin_density(a, lats_, lons_, per, center=HX, r0=70, r1=110):
    gidx=np.arange(len(a))//per
    p=a['pos'][:,2,:]+(a['pos'][:,3,:]-a['pos'][:,2,:])*FR
    inr,_=ring_frac(p[:,1],p[:,0],center,r0,r1)
    cnt=np.bincount(gidx[inr],minlength=len(lats_)*len(lons_)).reshape(len(lats_),len(lons_))
    return cnt/per   # P(in ring | origin), per grid point
OD={m:origin_density(a,lats,lons,1200) for m,a in SG.items()}
LL,LO=np.meshgrid(lats,lons,indexing='ij'); area=np.cos(np.radians(LL))
def summarize(od):
    post=od*area; post=post/post.sum()
    o=np.argsort(-post.ravel()); cm=np.cumsum(post.ravel()[o])
    def hpd_level(i,j):  # smallest HPD containing point
        r=np.where(o==i*len(lons)+j)[0][0]; return cm[r]
    res={}
    for name,la,lo in pts:
        i=np.argmin(abs(lats-la)); j=np.argmin(abs(lons-lo))
        dd=hav(la,lo,LL,LO); near=dd<50
        res[name]=dict(P_ring_given_origin=float(od[i,j]), hpd_level=float(hpd_level(i,j)), post_mass_within50km=float(post[near].sum()),
                       ratio_to_max=float(od[i,j]/od.max()))
    imax=np.unravel_index(np.argmax(post),post.shape)
    res['_mode']=dict(lat=float(lats[imax[0]]),lon=float(lons[imax[1]]),P_ring=float(od.max()))
    res['_edge_mass']=float(post[:, -2:].sum()+post[:2,:].sum()+post[-2:,:].sum())
    return res,post
SUMB={}
for m in OD: SUMB[m],_=summarize(OD[m]); print(m, json.dumps({k:{kk:round(vv,5) for kk,vv in v.items()} if isinstance(v,dict) else round(v,4) for k,v in SUMB[m].items()}))
