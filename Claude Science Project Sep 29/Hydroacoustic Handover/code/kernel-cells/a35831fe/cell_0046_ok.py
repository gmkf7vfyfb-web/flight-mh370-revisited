Tr=pd.read_csv(RK+'ranked_triples.csv')
def classify_sets(D, rxcols):
    D=D.copy()
    D['imp_t']=D.implied_impact_utc.map(lambda x: hms(x) if isinstance(x,str) else np.nan)
    D['time_cls']=D.imp_t.map(time_cls)
    D['loc_mass']=[fE(L,mass) if np.isfinite(L) else np.nan for L in D.locus_lat]
    D['loc_cls']=np.where(D.locus_lat.isna(),'no arc locus',np.where(D.loc_mass>=1e-3,'inside prior','outside prior (<0.1% mass within 1 deg)'))
    D['eta_min']=D.eta_level_locus*fE(D.locus_lat,Emed0)/fE(D.locus_lat,Eq99)
    D['eta_min_xF35A']=D.eta_min/ANCH
    D['energy_tier']=D.eta_min.map(tier)
    has=lambda r: lambda row: any(str(row[c])==r or r in str(row[c]).split('|') or r in str(row[c]) for c in rxcols)
    D['has_3250']=D.apply(has('3250'),axis=1); D['has_H08S']=D.apply(has('H08S'),axis=1)
    return D
Pc=classify_sets(P,['rx_a','rx_b']); Tc=classify_sets(Tr,['rxs'])
for nm,D in [('pairs',Pc),('triples',Tc)]:
    print(nm, len(D), 'with 3250:',D.has_3250.sum(),' with H08S:',D.has_H08S.sum(), ' neither:',(~D.has_3250&~D.has_H08S).sum())
    k=~D.has_3250&~D.has_H08S
    print(pd.crosstab(D[k].energy_tier, D[k].time_cls)); print(D[k].loc_cls.value_counts())
# pairs H08S airgun coincidence
def shot_dt(t): return (shots-t)[np.argmin(np.abs(shots-t))]
for c in ['a','b']:
    Pc['dtshot_'+c]=[shot_dt(hms(t)) if r=='H08S' else np.nan for r,t in zip(Pc['rx_'+c],Pc['t_'+c])]
h=Pc[Pc.has_H08S]; print('H08S member within 1.5 s of shot:', ((h.dtshot_a.abs()<=1.5)|(h.dtshot_b.abs()<=1.5)).mean())