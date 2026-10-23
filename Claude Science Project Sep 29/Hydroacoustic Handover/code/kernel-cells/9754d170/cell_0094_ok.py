
src=np.load('/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-held-out.npz')
cols=list(src['state_columns']); print(cols)
S=src['state']; c={n:i for i,n in enumerate(cols)}
KE=S[:,c['kinetic_energy_j']]; w=np.asarray(src['w_flight'],float); w/=w.sum()
def wq(x,w,qs):
    o=np.argsort(x); cw=np.cumsum(w[o]); return [float(x[o][np.searchsorted(cw,q)]) for q in qs]
print('KE GJ q',[round(v/1e9,3) for v in wq(KE,w,[0,0.05,0.5,0.95,1])])
for k in cols:
    if 'speed' in k or 'vertical' in k or 'gamma' in k or 'angle' in k or 'mass' in k:
        print(k, [round(v,3) for v in wq(S[:,c[k]],w,[0,0.05,0.5,0.95,1])])
print([k for k in src.files])
