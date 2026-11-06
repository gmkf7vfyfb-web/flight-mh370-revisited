import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
import sigcorr as SC
from scipy.stats import genpareto
N=np.load('corr_norm.npz')
SPEC={'L_d0':'d0','L_d1':'d1','S_d1':'s_d1','S_d2':'s_d2','L_d2':'d2'}
rows=[]
for kind,sd_,cd_ in (('rnd','scores_rnd','corr_rnd'),('gauss','scores_gauss','corr_gauss')):
    for fn in sorted(glob.glob(f'{cd_}/*.npz')):
        k=os.path.basename(fn)[:-4]; st=k[:4]; pre='' if kind=='rnd' else 'g'
        zc=np.load(fn); zs=np.load(f'{sd_}/{k}.npz')
        za,zi=SC.corr_stats(zc['z'],N[pre+st+'_mu'],N[pre+st+'_sd'],zc['Wb']); c=zc['c']; pe=zc['pe']
        t=zs['t']; bad=zs['gap'].astype(bool)
        A={s:np.asarray(zs[v],float) for s,v in SPEC.items()}
        for b0 in np.arange(c[0],c[-1]-120,120.0):
            m=(c>=b0)&(c<b0+120); f=(t>=b0)&(t<b0+120)
            if m.sum()<20 or f.sum()<200 or bad[f].any() or not np.isfinite(za[m]).all(): continue
            if any(not np.isfinite(A[s][f]).all() for s in A): continue
            rows.append(dict(kind=kind,st=st,rec=k,b0=b0,C_any=za[m].max(),C_imp=zi[m].max(),E_pers=np.nanmax(pe[m]),**{s:A[s][f].max() for s in A}))
B=pd.DataFrame(rows); B.to_csv('joint_background.csv',index=False)
print(B.groupby(['kind','st']).size())
