ZS=[np.load(f) for f in ('rc2-wp-a.npz','rc2-wp-b.npz','rc2-other.npz')]
seedkeys=[(Zf,k[:-2]) for Zf in ZS for k in Zf.files if k.endswith('|c')]
FAMN=['all','A1','A2','B']
def pooled2(D,v):
    lw=np.array([float(Zf[pre+'|c'])+float(Zf[f'{pre}|{D}|{v}|s']) for Zf,pre in seedkeys]); M=lw.max(); sc=np.exp(lw-M)
    g=lambda key: np.array([Zf[f'{pre}|{D}|{v}|{key}'] for Zf,pre in seedkeys])
    out=dict(sc=sc,M=M,sum=g('sum')*sc,sum2=g('sum2')*sc**2,fam=g('fam')*sc[:,None],thist=g('thist')*sc[:,None],strata=np.array([pre.split('|')[0] for Zf,pre in seedkeys]))
    for f in FAMN:
        out['sum_'+f]=out['sum'] if f=='all' else g('sum_'+f)*sc
        for m in MODELS:
            suf='' if f=='all' else '_'+f
            out[f'vec_{m}{suf}']=g(f'vec_{m}{suf}')*sc[:,None]; out[f'den_{m}{suf}']=g(f'den_{m}{suf}')*sc
    if v!='none':
        for k in ('din','parents99','lat_mean','lon_mean','rows99'):
            kk={'din':'d_inside_km'}.get(k,k); out[k]=g(kk)*(sc[:,None] if k=='din' else 1)
    return out
P2={(D,v):pooled2(D,v) for D in Ds for v in VARS}
def lnE2(pp,m,opt='none',fam='all',Ln=None,idx=None):
    """ln of conditional mean L; rows outside drift support carried at their seed's (conditional, family) weighted mean."""
    Ln=node_L(m,'h50',opt) if Ln is None else Ln; suf='' if fam=='all' else '_'+fam
    vec=pp[f'vec_{m}{suf}']; den=pp[f'den_{m}{suf}']; tot=pp['sum_'+fam]
    if idx is not None: vec,den,tot=vec[idx],den[idx],tot[idx]
    num=(vec*np.nan_to_num(Ln)[None,:]).sum(1); ok=den>0
    seedmean=np.where(ok,num/np.where(ok,den,1),0.0)
    return np.log((tot[ok]*seedmean[ok]).sum()/tot[ok].sum())+LREF
for D in ['D0']:
    for o in ['none','B','populated']:
        print(o,[ (round(lnE2(P2[(D,'none')],m,OPT[o]),3), round(aus['cells'][D][f'{OPT[o]}|{m}']['dlnZ_drift'],3)) for m in MODELS])
