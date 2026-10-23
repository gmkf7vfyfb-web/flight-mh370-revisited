ANCH_OLD=2.1e-4; ANCH=2.26e-3
w0=W['D0']
grid=np.arange(-41.5,-19.4,0.25); Emed0=[];Eq99=[];mass=[]
md=w0>0; tot=w0.sum()
for g in grid:
    k=md&(np.abs(lat-g)<=1)
    if k.sum()>=20: Emed0.append(wq(E[k],w0[k],.5)); 
    else: Emed0.append(np.nan)
    k2=m&(np.abs(lat-g)<=1)
    Eq99.append(wq(E[k2],wall[k2],.99) if k2.sum()>=20 else np.nan)
    mass.append(wall[k2].sum()/wall[m].sum())
Emed0=np.array(Emed0);Eq99=np.array(Eq99);mass=np.array(mass)
fE=lambda L,arr_: np.interp(L,grid,arr_)
def tier(eta):
    if not np.isfinite(eta): return 'no level (blocked receiver or not computable)'
    r=eta/ANCH
    if eta>1: return 'impossible (coupling > 1)'
    if r>100: return 'not feasible (>100x F-35A)'
    if r>10: return 'strained (10-100x F-35A)'
    return 'feasible (<=10x F-35A)'
# singles
s['t']=s.time_utc.map(hms)
s['imp_lat']=s.implied_source.str.extract(r'([\d.]+)S').astype(float).mul(-1)
s['imp_t']=s.implied_impact_utc.map(lambda x: hms(x) if isinstance(x,str) else np.nan)
s['eta_min']=s.eta_needed*1.1306e9/fE(s.imp_lat,Eq99)
s['eta_min_xF35A']=s.eta_min/ANCH
s['energy_tier']=s.eta_min.map(tier)
s['dt_shot']=[ (shots-t)[np.argmin(np.abs(shots-t))] if r=='H08S' else np.nan for r,t in zip(s.rx,s.t)]
def time_cls(t):
    if not np.isfinite(t): return 'no implied time'
    if t<hms('00:19:29'): return 'impossible (before 00:19:29)'
    if t>hms('00:47:51'): return 'outside 99% of prior'
    return 'inside'
s['time_cls']=s.imp_t.map(time_cls)
print(s.energy_tier.value_counts()); print(s.time_cls.value_counts())
print(s.groupby('rx').energy_tier.value_counts().unstack(fill_value=0))
print(s[['rx','eta_needed','eta_min','eta_min_xF35A']].groupby('rx').min())