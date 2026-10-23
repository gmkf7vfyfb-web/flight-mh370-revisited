tau_all=S['tau90_s']; lon_all=S['lon']
RX4=['H01W','H08S','3315','3376','3274','3275']
ETAS=[('1e-4',1e-4),('old value 2.1e-4 (wrong)',2.1e-4),('1e-3',1e-3),('F-35A 2.26e-3',2.26e-3),('1e-2',1e-2)]
rng=np.random.default_rng(7)
lev={}
for k,cd in CANDS.items():
    L=cd['lat']; msk=m&(np.abs(lat-L)<=0.5)&(np.abs(tu-cd['t0'])<=600)
    idx=np.where(msk)[0]; w=wall[idx]; n=len(idx)
    pick=rng.choice(idx,size=min(20000,n),p=w/w.sum(),replace=True)
    Eq=np.quantile(E[pick],[.05,.5,.95])
    base,ti=M.level_base(lat[pick],E[pick],np.nan_to_num(tau_all[pick],nan=3.3))
    lev[k]=dict(n=n,Eq=Eq,base={r:base[r] for r in RX4},ti=ti)
    print(k,f"rows {n}, E q05/50/95 {Eq/1e9}", {r:np.round(np.quantile(base[r],[.05,.5,.95]),1) for r in RX4})
# M1b L50 at alpha 0.05 per receiver (tau-cell median)
L50={r:np.nanmedian(M.pd_par[(r,0.05)][0]) for r in RX4}; print(L50)