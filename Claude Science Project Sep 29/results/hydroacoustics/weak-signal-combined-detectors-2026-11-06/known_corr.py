import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
import sigdet as SD, sigcorr as SC, pmap
from score_records import load
from obspy import UTCDateTime
from multiprocessing import Pool
from scipy.stats import binomtest
RD='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records'
CN=np.load('corr_norm.npz')
kc=pd.read_csv('known_events_control.csv')
EV={}
for st in ('H01W','H08S'):
    d=pd.read_csv(f'bc/out/eq_{st}_events.csv').set_index('evid'); EV[st]=d
def run(r):
    st,rec,evid=r
    t0,x=load(f'{RD}/{rec}.mseed',st); tp=UTCDateTime(EV[st].loc[evid].t_pred)-t0
    c=np.arange(tp-40,tp+80.01,5.0); c=c[(c>330)&(c<len(x)/SD.FS-330)]
    if len(c)<10: return None
    z=SC.local_lags(x,c); za,zi=SC.corr_stats(z,CN[st+'_mu'],CN[st+'_sd'],SC.record_bank(x))
    pe=SC.persistence(SC.envelope_db(x),c,SC.TAU[st])
    zs=np.load(f'scores/{rec}.npz'); t=zs['t']; m=(t>=tp-40)&(t<=tp+80)
    return dict(st=st,rec=rec,evid=evid,C_any=np.nanmax(za),C_imp=np.nanmax(zi),E_pers=np.nanmax(pe),L_d0=float(np.nanmax(zs['d0'][m])),L_d1=float(np.nanmax(zs['d1'][m])),S_d1=float(np.nanmax(zs['s_d1'][m])))
if __name__=='__main__':
    rows=[(r.st,r.rec,r.evid) for r in kc.itertuples()]
    with Pool(16) as p: out=[o for o in p.map(run,rows,chunksize=4) if o]
    K=pd.DataFrame(out).merge(kc[['rec','snr_db']],on='rec')
    B=pd.read_csv('joint_background.csv'); P=pmap.PMap(B,'rnd')
    for st in ('H01W','H08S'):
        m=K.st==st
        for s in pmap.STATS: K.loc[m,'p_'+s]=P.p(st,s,K.loc[m,s].values)
        K.loc[m,'p_COMB']=None
        F=P.fisher(st,{s:K.loc[m,s].values for s in pmap.COMB}); Fs=P.f[(st,'COMB')]
        K.loc[m,'p_COMB']=(len(Fs)-np.searchsorted(Fs,F)+1)/(len(Fs)+1)
    K.to_csv('known_events_corr.csv',index=False)
    K['strength']=pd.cut(K.snr_db,[-1,10,15,20,99],labels=['<10','10-15','15-20','>20'])
    D=['L_d0','L_d1','S_d1','C_any','C_imp','E_pers','COMB']
    for a in (0.05,0.2):
        print(f'\nfraction detected at per-look background chance < {a}')
        print(K.groupby(['st','strength']).apply(lambda g: pd.Series({'n':len(g),**{d:round((g['p_'+d].astype(float)<a).mean(),2) for d in D}})).to_string())
        for st,g in K.groupby('st'):
            for d in ('C_imp','S_d1','COMB'):
                x=g['p_'+d].astype(float)<a; y=g['p_L_d0']<a; n1=int((x&~y).sum()); n2=int((~x&y).sum())
                print(st,d,'vs band energy: found only by it',n1,'only by band energy',n2,'McNemar p',round(binomtest(n1,n1+n2).pvalue,4) if n1+n2 else 1)
