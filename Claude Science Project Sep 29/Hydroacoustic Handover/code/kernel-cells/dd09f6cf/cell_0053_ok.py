import glob, re
from scipy.special import logsumexp
PF=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/family-shares-run-j.json'))['p_core']
STR=['run-j-waypoints','run-j-free','run-j-repro-radar','run-j-descent-climb']
DK=[f'D{d}' for d in range(6)]
Z={}
for s in STR:
    fl=sorted(glob.glob(f'red/{s}_*.npz'),key=lambda f:int(re.findall(r'_(\d+)\.npz',f)[0]))
    Z[s]=[dict(np.load(f)) for f in fl]
print({s:len(v) for s,v in Z.items()}, PF)
MASKS=['strip']+[f'X{r}' for r in (50,100,200,400)]+[f'H{r}' for r in (50,100,200,400)]
AK=['Tcore','Twide','Ccore','Cwide']; LSV=['s00','s05','s25','s50','x05']
def seedlist(d, extra=None):
    """list of (stratum, seed index, log factor) with factor = ln(P/K)+s (+ sa for acoustic)"""
    L=[]
    for s in STR:
        K=len(Z[s])
        for i,z in enumerate(Z[s]):
            if int(z[f'{d}|valid']): 
                c=np.log(PF[s]/K)+float(z[f'{d}|s'])
                if extra: c+=float(z[f'{d}|{extra}|sa'])
                L.append((s,i,c))
    return L
def pooled(d, keys, extra=None, idx=None):
    L=seedlist(d,extra); 
    if idx is not None: L=[L[i] for i in idx]
    cmax=max(c for *_,c in L)
    return {k: sum(np.exp(c-cmax)*Z[s][i][k] for s,i,c in L) for k in keys}, cmax, L
res={}
for d in DK:
    r={}
    keys=[f'{d}|M',f'{d}|M2']+[f'{d}|all|LS|{v}' for v in LSV]+[f'{d}|all|fam|{f}' for f in ('A1','A2','B')]
    for mk in MASKS: keys+= [f'{d}|{mk}|{x}' for x in ('M','M2','covOI18_mean')]+[f'{d}|{mk}|LS|{v}' for v in LSV]+[f'{d}|{mk}|fam|{f}' for f in ('A1','A2','B')]
    P_,cm,Ls=pooled(d,keys)
    # M2 scale: e^{2(c)} not e^{c}; recompute ESS with proper scale
    def ess(k2,k1):
        num=sum(np.exp(c-cm)*Z[s][i][k1] for s,i,c in Ls)**2; den=sum(np.exp(2*(c-cm))*Z[s][i][k2] for s,i,c in Ls); return num/den if den>0 else 0
    M=P_[f'{d}|M']; r['ESS_all']=ess(f'{d}|M2',f'{d}|M')
    r['Ls_all']={v:P_[f'{d}|all|LS|{v}']/M for v in LSV}
    for mk in MASKS:
        Mm=P_[f'{d}|{mk}|M']; r[mk]={'mass':Mm/M,'ESS':ess(f'{d}|{mk}|M2',f'{d}|{mk}|M'),
           'nrows':sum(int(Z[s][i][f'{d}|{mk}|nrows']) for s,i,c in Ls),'nparents':sum(int(Z[s][i][f'{d}|{mk}|nparents']) for s,i,c in Ls),
           'covOI18':P_[f'{d}|{mk}|covOI18_mean']/Mm if Mm>0 else np.nan,
           'Ls':{v:(P_[f'{d}|{mk}|LS|{v}']/Mm if Mm>0 else np.nan) for v in LSV},
           'Ls_comp':{v:(P_[f'{d}|all|LS|{v}']-P_[f'{d}|{mk}|LS|{v}'])/(M-Mm) for v in LSV},
           'fam':{f:(P_[f'{d}|{mk}|fam|{f}']/Mm if Mm>0 else np.nan) for f in ('A1','A2','B')}}
    for ak in AK:
        keys2=[f'{d}|{ak}|W',f'{d}|{ak}|in_strip',f'{d}|{ak}|covOI18_mean']+[f'{d}|{ak}|LS|{v}' for v in LSV]+[f'{d}|{ak}|fam|{f}' for f in ('A1','A2','B')]
        Q,cq,Lq=pooled(d,keys2,extra=ak)
        num=sum(np.exp(c-cq)*Z[s][i][f'{d}|{ak}|W'] for s,i,c in Lq)**2; den=sum(np.exp(2*(c-cq))*Z[s][i][f'{d}|{ak}|W2'] for s,i,c in Lq)
        W=Q[f'{d}|{ak}|W']
        r[ak]={'ESS':num/den,'in_strip':Q[f'{d}|{ak}|in_strip']/W,'covOI18':Q[f'{d}|{ak}|covOI18_mean']/W,
               'Ls':{v:Q[f'{d}|{ak}|LS|{v}']/W for v in LSV},'fam':{f:Q[f'{d}|{ak}|fam|{f}']/W for f in ('A1','A2','B')},
               'lnZ_ratio_to_core': float(np.log(W)+cq - (np.log(M)+cm))}
    res[d]=r
for d in DK:
    r=res[d]; print(d, 'strip mass %.4g ESS %.0f rows %d par %d covOI %.3f | Ls05 strip %.3f comp %.3f all %.3f'%(r['strip']['mass'],r['strip']['ESS'],r['strip']['nrows'],r['strip']['nparents'],r['strip']['covOI18'],r['strip']['Ls']['s05'],r['strip']['Ls_comp']['s05'],r['Ls_all']['s05']))
    for ak in AK: print('   ',ak,'ESS %.1f in_strip %.3f covOI %.3f Ls05 %.3f x05 %.3f'%(r[ak]['ESS'],r[ak]['in_strip'],r[ak]['covOI18'],r[ak]['Ls']['s05'],r[ak]['Ls']['x05']))