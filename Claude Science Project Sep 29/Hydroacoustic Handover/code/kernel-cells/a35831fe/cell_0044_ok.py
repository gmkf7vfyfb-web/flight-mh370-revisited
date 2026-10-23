S=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/sample.npz')
lat=S['lat']; E=S['E_j']; tu=S['t_unix']-T0
W={o:S['w_'+o] for o in ['D0','D2','D3','D4']}
wall=sum(W[o]/W[o].sum() for o in W)/4   # option-averaged
def wq(x,w,q):
    o=np.argsort(x); c=np.cumsum(w[o]); c/=c[-1]; return np.interp(q,c,x[o])
m=wall>0
print('E q01,q05,q50,q95,q99,max (GJ):', [round(wq(E[m],wall[m],q)/1e9,2) for q in [.01,.05,.5,.95,.99]], round(E[m].max()/1e9,2))
print('impact time q005,q01,q50,q99,q995,max:', [fmt(wq(tu[m],wall[m],q)) for q in [.005,.01,.5,.99,.995]], fmt(tu[m].max()), fmt(tu[m].min()))
print('lat q005,q01,q99,q995:', [round(wq(lat[m],wall[m],q),2) for q in [.005,.01,.5,.99,.995]])
bins=np.arange(-42,-19,1.0); Etab={}
for b in bins:
    k=m&(np.abs(lat-b)<=1)
    if k.sum()>50: Etab[b]=(wq(E[k],wall[k],.5), wq(E[k],wall[k],.99), wall[k].sum()/wall[m].sum())
for b,v in Etab.items(): print(b, round(v[0]/1e9,2), round(v[1]/1e9,2), round(v[2],4))