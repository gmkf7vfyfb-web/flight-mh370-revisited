Lc=Lgrid[(REF_A,'csiro')].copy(); okc=np.isfinite(Lc); Lc0=np.where(okc,Lc,0)
BOOT={}
for d in DK:
    rows=seed_scalars(d); base=ratios(rows); bys={s:[r for r in rows if r['s']==s] for s in STR}; bs_=[]
    for b in range(300):
        rr=[]
        for s in STR:
            L_=bys[s]; rr+=[L_[j] for j in rng.integers(0,len(L_),len(L_))]
        bs_.append(ratios(rr))
    BOOT[d]={k:{'seabed':base[k][0],'seabed_sd':float(np.nanstd([x[k][0] for x in bs_])),'surface':base[k][1],'surface_sd':float(np.nanstd([x[k][1] for x in bs_]))} for k in base}
ess_tab=pd.DataFrame({d:{**{f'ESS {ak}':res[d][ak]['ESS'] for ak in AK},'ESS strip':res[d]['strip']['ESS'],'mass strip':res[d]['strip']['mass'],'ESS X200':res[d]['X200']['ESS'],'mass X200':res[d]['X200']['mass'],'ESS H50':res[d]['H50']['ESS'],'mass H50':res[d]['H50']['mass']} for d in DK}).T
print(ess_tab.round(5).to_string())
print({d:{k:'%.2f±%.2f / %.2f±%.2f'%(v['seabed'],v['seabed_sd'],v['surface'],v['surface_sd']) for k,v in BOOT[d].items() if k in('strip','Tcore','Ccore')} for d in DK})