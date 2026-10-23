MP=pickle.load(open('kh/out/maps.pkl','rb')); print(len(MP)); print([k for k in MP][:5])
ni,nj=W.grid_shape(W.LOC); niw,njw=W.grid_shape(W.WIDE)
def getmap(pool,k,vn,grid='loc'):
    s,h=MP[f'{pool}|{k}|{vn}|{grid}']; n=(ni*nj) if grid=='loc' else (niw*njw)
    return h[:n].reshape((ni,nj) if grid=='loc' else (niw,njw)), h[n]/h.sum()
def hpd_levels(H,qs=(0.5,0.9,0.99)):
    v=np.sort(H.ravel())[::-1]; c=np.cumsum(v)/v.sum(); return [v[min(np.searchsorted(c,q),len(v)-1)] for q in qs]
for k in HK[:1]:
    for vn in ['T1.0','C1.0','prior']:
        H,out=getmap('main',k,vn); print(vn, out, (H>0).sum())