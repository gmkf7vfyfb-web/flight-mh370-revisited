rng=np.random.default_rng(18102026)
Lc=Lgrid[('0.012','csiro')].copy(); okc=np.isfinite(Lc); Lc0=np.where(okc,Lc,0)
def seed_scalars(d):
    rows=[]
    for s in STR:
        K=len(Z[s])
        for i,z in enumerate(Z[s]):
            if not int(z[f'{d}|valid']): continue
            c=np.log(PF[s]/K)+float(z[f'{d}|s'])
            r={'s':s,'c':c,'M':z[f'{d}|M'],'LSall':z[f'{d}|all|LS|s05'],'Sall':z[f'{d}|hist|all']@Lc0,'Hall':z[f'{d}|hist|all'][okc].sum()}
            for mk in ['strip','X200']:
                r[mk+'M']=z[f'{d}|{mk}|M']; r[mk+'LS']=z[f'{d}|{mk}|LS|s05']; r[mk+'S']=z[f'{d}|hist|{mk}']@Lc0; r[mk+'H']=z[f'{d}|hist|{mk}'][okc].sum()
            for ak in AK:
                ca=c+float(z[f'{d}|{ak}|sa']); r[ak+'c']=ca; r[ak+'W']=z[f'{d}|{ak}|W']; r[ak+'LS']=z[f'{d}|{ak}|LS|s05']; r[ak+'S']=z[f'{d}|hist|{ak}']@Lc0; r[ak+'H']=z[f'{d}|hist|{ak}'][okc].sum()
            rows.append(r)
    return rows
def ratios(rows):
    cm=max(r['c'] for r in rows); w=np.array([np.exp(r['c']-cm) for r in rows]); g=lambda k: float((w*np.array([r[k] for r in rows])).sum())
    out={}
    M=g('M'); LSall=g('LSall'); Sall=g('Sall')/g('Hall')
    for mk in ['strip','X200']:
        Mm=g(mk+'M'); ls=g(mk+'LS')/Mm; lsc=(LSall-g(mk+'LS'))/(M-Mm); su=g(mk+'S')/g(mk+'H'); m=Mm/M; suc=(Sall-m*su)/(1-m)
        out[mk]=(np.log(ls/lsc), np.log(su/suc))
    for ak in AK:
        ca=max(r[ak+'c'] for r in rows); wa=np.array([np.exp(r[ak+'c']-ca) for r in rows]); ga=lambda k: float((wa*np.array([r[k] for r in rows])).sum())
        W=ga(ak+'W'); ls=ga(ak+'LS')/W; su=ga(ak+'S')/ga(ak+'H')
        # complement: rest of run J ~ all rows minus acoustic-selected; acoustic weight share negligible -> use strip complement
        Mm=g('stripM'); lsc=(LSall-g('stripLS'))/(M-Mm); m=Mm/M; suc=(Sall-m*(g('stripS')/g('stripH')))/(1-m)
        out[ak]=(np.log(ls/lsc), np.log(su/suc))
    return out
BOOT={}
for d in DK:
    rows=seed_scalars(d); base=ratios(rows)
    bys={s:[r for r in rows if r['s']==s] for s in STR}
    bs_=[]
    for b in range(300):
        rr=[]
        for s in STR:
            L_=bys[s]; rr+= [L_[j] for j in rng.integers(0,len(L_),len(L_))]
        try: bs_.append(ratios(rr))
        except Exception: pass
    BOOT[d]={k:{'seabed':base[k][0],'seabed_sd':float(np.nanstd([x[k][0] for x in bs_])),'surface':base[k][1],'surface_sd':float(np.nanstd([x[k][1] for x in bs_]))} for k in base}
    print(d, {k:'sb %.2f±%.2f su %.2f±%.2f'%(v['seabed'],v['seabed_sd'],v['surface'],v['surface_sd']) for k,v in BOOT[d].items()})