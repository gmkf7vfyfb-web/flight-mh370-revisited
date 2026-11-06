import sys, os; sys.path.insert(0, os.getcwd())
import numpy as np, pandas as pd, known_corr as KC, sigdet as SD, sigcorr as SC, pmap
from score_records import load
from obspy import UTCDateTime
from multiprocessing import Pool
def run(r):
    st,rec,evid=r
    t0,x=load(f'{KC.RD}/{rec}.mseed',st); tp=UTCDateTime(KC.EV[st].loc[evid].t_pred)-t0
    T=len(x)/SD.FS; to=tp-600 if tp-600>380 else tp+600
    if to+80>T-330: return None
    c=np.arange(to-40,to+80.01,5.0)
    z=SC.local_lags(x,c); za,zi=SC.corr_stats(z,KC.CN[st+'_mu'],KC.CN[st+'_sd'],SC.record_bank(x))
    pe=SC.persistence(SC.envelope_db(x),c,SC.TAU[st])
    zs=np.load(f'scores/{rec}.npz'); t=zs['t']; m=(t>=to-40)&(t<=to+80)
    if zs['gap'][m].any(): return None
    return dict(st=st,rec=rec,C_any=np.nanmax(za),C_imp=np.nanmax(zi),E_pers=np.nanmax(pe),L_d0=float(np.nanmax(zs['d0'][m])),L_d1=float(np.nanmax(zs['d1'][m])),S_d1=float(np.nanmax(zs['s_d1'][m])))
if __name__=='__main__':
    rows=[(r.st,r.rec,r.evid) for r in KC.kc.itertuples()]
    with Pool(16) as p: out=[o for o in p.map(run,rows,chunksize=4) if o]
    O=pd.DataFrame(out); B=pd.read_csv('joint_background.csv'); P=pmap.PMap(B,'rnd')
    for st in ('H01W','H08S'):
        m=O.st==st
        for s in pmap.STATS: O.loc[m,'p_'+s]=P.p(st,s,O.loc[m,s].values)
        F=P.fisher(st,{s:O.loc[m,s].values for s in pmap.COMB}); Fs=P.f[(st,'COMB')]
        O.loc[m,'p_COMB']=(len(Fs)-np.searchsorted(Fs,F)+1)/(len(Fs)+1)
    O.to_csv('known_events_corr_offlook.csv',index=False)
    D=['L_d0','L_d1','S_d1','C_any','C_imp','E_pers','COMB']
    for a in (0.05,0.2):
        print(f'off-arrival false-alarm rate in the same earthquake records, per-look chance < {a}')
        print(O.groupby('st').apply(lambda g: pd.Series({'n':len(g),**{d:round((g['p_'+d].astype(float)<a).mean(),3) for d in D}})).to_string())
