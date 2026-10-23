rng=np.random.default_rng(11)
NREP=300
# transport-noise node perturbations (mean-preserving lognormal per 1-deg band), shared by reference and conditional
sdn={m: np.array([nsb[m].get(str(int(np.floor(alat_n[k]))), np.nan) for k in range(NC)]) for m in ('glorys12','globcurrent')}
pert={m: [np.exp(rng.normal(-np.nan_to_num(sdn[m])**2/2, np.nan_to_num(sdn[m]))) for _ in range(NREP)] for m in sdn}
def Lpert(m,opt,r):
    if m=='mean':
        a,b=Lpert('glorys12',opt,r),Lpert('globcurrent',opt,r); return np.where(np.isfinite(a)&np.isfinite(b),0.5*(a+b),np.nan)
    return node_L(m,'h50',opt)*pert[m][r]
strata_names=sorted(set(P[('D0','none')]['strata']))
def boot_idx():
    st=P[('D0','none')]['strata']; idx=[]
    for s in strata_names:
        ii=np.where(st==s)[0]; idx.append(rng.choice(ii,len(ii),replace=True))
    return np.concatenate(idx)
BOOT=[boot_idx() for _ in range(300)]
rows=[]
for D in Ds:
    ref=P[(D,'none')]
    for v in VARS[1:]:
        pc=P[(D,v)]
        ess=pc['sum'].sum()**2/pc['sum2'].sum()
        fam=pc['fam'].sum(0); famsh=fam/fam.sum()
        strat={s: float(pc['sum'][pc['strata']==s].sum()/pc['sum'].sum()) for s in strata_names}
        lnZv=float(np.log(pc['sum'].sum())+pc['M'] - (np.log(ref['sum'].sum())+ref['M']))  # ln E_runJ[L_acoustic] (unnormalised acoustic density)
        for m in MODELS:
            for o,oo in OPT.items():
                c_=lnE(pc,m,oo); r_=lnE(ref,m,oo); llr=c_-r_
                tn=[lnE(pc,m,oo,Ln=Lpert(m,oo,r))-lnE(ref,m,oo,Ln=Lpert(m,oo,r)) for r in range(0,NREP,3)]
                bs=[lnE(pc,m,oo,idx=b)-lnE(ref,m,oo,idx=b) for b in BOOT[:100]]
                rows.append(dict(D=D,variant=v,model=m,option=o,lnE_cond=c_,lnE_ref=r_,LLR=llr,sd_transport=float(np.std(tn)),sd_seed_boot=float(np.std(bs)),
                                 sd_total=float(np.hypot(np.std(tn),np.std(bs))),ESS=ess,valid_share=float(pc['den_'+m].sum()/pc['sum'].sum()),
                                 share_A1=famsh[1],share_A2=famsh[2],share_B=famsh[3],share_other=1-famsh[1]-famsh[2]-famsh[3],
                                 **{f'stratum_{s}':strat[s] for s in strata_names}, ln_mean_acoustic_density_vs_runJ=lnZv))
RC=pd.DataFrame(rows)
print(RC[(RC.D=='D0')&(RC.model=='mean')][['variant','option','LLR','sd_transport','sd_seed_boot','ESS','valid_share','share_A1','share_A2','share_B']].round(3).to_string())
