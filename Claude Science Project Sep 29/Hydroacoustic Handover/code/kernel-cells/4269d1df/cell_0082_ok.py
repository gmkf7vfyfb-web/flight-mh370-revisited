from scipy.special import logsumexp
ZS=[np.load(f) for f in ('rc-wp-a.npz','rc-wp-b.npz','rc-other.npz')]
seedkeys=[]
for Zf in ZS:
    for k in Zf.files:
        if k.endswith('|c'): seedkeys.append((Zf,k[:-2]))
print(len(seedkeys))
Ds=[f'D{d}' for d in range(6)]; VARS=['none','T_core','T_wide','C_core','C_wide']
MODELS=('glorys12','globcurrent','mean')
def pooled(D,v):
    lw=[]; vecs={m:[] for m in MODELS}; dens={m:[] for m in MODELS}; s2=[]; fam=[]; th=[]; din=[]; strata=[]; par=0; lat_m=[]; lon_m=[]
    for Zf,pre in seedkeys:
        k=f'{pre}|{D}|{v}'; c=float(Zf[pre+'|c']); s=float(Zf[k+'|s']); lw.append(c+s)
    lw=np.array(lw); M=lw.max(); sc=np.exp(lw-M)
    out=dict(sc=sc,M=M)
    out['sum']=np.array([float(Zf[f'{pre}|{D}|{v}|sum']) for Zf,pre in seedkeys])*sc
    out['sum2']=np.array([float(Zf[f'{pre}|{D}|{v}|sum2']) for Zf,pre in seedkeys])*sc**2
    for m in MODELS:
        out['vec_'+m]=np.array([Zf[f'{pre}|{D}|{v}|vec_{m}'] for Zf,pre in seedkeys])*sc[:,None]
        out['den_'+m]=np.array([float(Zf[f'{pre}|{D}|{v}|den_{m}']) for Zf,pre in seedkeys])*sc
    out['fam']=np.array([Zf[f'{pre}|{D}|{v}|fam'] for Zf,pre in seedkeys])*sc[:,None]
    out['thist']=np.array([Zf[f'{pre}|{D}|{v}|thist'] for Zf,pre in seedkeys])*sc[:,None]
    if v!='none':
        out['din']=np.array([Zf[f'{pre}|{D}|{v}|d_inside_km'] for Zf,pre in seedkeys])*sc[:,None]
        out['parents99']=np.array([int(Zf[f'{pre}|{D}|{v}|parents99']) for Zf,pre in seedkeys])
        out['lat_mean']=np.array([float(Zf[f'{pre}|{D}|{v}|lat_mean']) for Zf,pre in seedkeys])
        out['lon_mean']=np.array([float(Zf[f'{pre}|{D}|{v}|lon_mean']) for Zf,pre in seedkeys])
    out['strata']=np.array([pre.split('|')[0] for Zf,pre in seedkeys])
    return out
P={(D,v):pooled(D,v) for D in Ds for v in VARS}
def lnE(pp,m,opt='none',Ln=None,idx=None):
    Ln=node_L(m,'h50',opt) if Ln is None else Ln
    vec=pp['vec_'+m] if idx is None else pp['vec_'+m][idx]; den=pp['den_'+m] if idx is None else pp['den_'+m][idx]
    return np.log(np.nansum(vec.sum(0)*np.nan_to_num(Ln))/den.sum())+LREF
# validation vs aus160 reference
for D in ['D0','D3']:
    for o,oo in OPT.items():
        print(D,o,[ (round(lnE(P[(D,'none')],m,oo),3), round(aus['cells'][D][f'{oo}|{m}']['dlnZ_drift'],3)) for m in MODELS])
