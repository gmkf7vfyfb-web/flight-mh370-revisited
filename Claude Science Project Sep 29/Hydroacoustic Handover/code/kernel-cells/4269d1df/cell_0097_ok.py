import time
t0=time.time()
LPcache={}
def LP(m,oo,r):
    k=(m,oo,r)
    if k not in LPcache: LPcache[k]=Lpert(m,oo,r)
    return LPcache[k]
LN={(m,oo):node_L(m,'h50',oo) for m in MODELS for oo in OPT2.values()}
rows=[]
REPS=range(0,NREP,3)
for D in Ds:
    ref=P2[(D,'none')]
    for v in VARS[1:]:
        pc=P2[(D,v)]; ess=pc['sum'].sum()**2/pc['sum2'].sum()
        famw={f: float(pc['sum_'+f].sum()/pc['sum'].sum()) for f in FAMN}
        for m in MODELS:
            for o,oo in OPT2.items():
                for f in FAMN:
                    if famw[f]<=0: continue
                    c_=lnE2(pc,m,oo,f,Ln=LN[(m,oo)]); r_=lnE2(ref,m,oo,f,Ln=LN[(m,oo)])
                    tn=[lnE2(pc,m,oo,f,Ln=LP(m,oo,r))-lnE2(ref,m,oo,f,Ln=LP(m,oo,r)) for r in REPS]
                    bs=[lnE2(pc,m,oo,f,Ln=LN[(m,oo)],idx=b)-lnE2(ref,m,oo,f,Ln=LN[(m,oo)],idx=b) for b in BOOT[:100]] if f=='all' else []
                    bs=[x for x in bs if np.isfinite(x)]
                    rows.append(dict(D=D,branch=v.split('_')[0],bearing_sd=('0.5 deg' if v.endswith('core') else '1.0 deg'),model=m,australia=o,family=f,
                        lnE_cond=c_,lnE_runJ=r_,LLR=c_-r_,sd_transport=float(np.std(tn)),sd_seed=float(np.std(bs)) if bs else np.nan,
                        ESS_branch=ess,family_share_cond=famw[f],family_share_runJ=float(ref['sum_'+f].sum()/ref['sum'].sum())))
RC2=pd.DataFrame(rows); RC2['sd_total']=np.sqrt(RC2.sd_transport**2+RC2.sd_seed.fillna(0)**2)
print(time.time()-t0, len(RC2))
print(RC2[(RC2.D=='D0')&(RC2.bearing_sd=='0.5 deg')&(RC2.family=='all')&(RC2.model=='mean')][['branch','australia','LLR','sd_transport','sd_seed']].round(2).to_string())
