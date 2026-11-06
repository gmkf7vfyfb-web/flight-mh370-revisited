import pandas as pd, numpy as np
from scipy.stats import binomtest
bg=pd.read_csv('background_looks.csv'); kn=pd.read_csv('known_events_raw.csv')
# add shape-only discrimination stats to known/background (S_d2 not stored in first pass: recompute from npz)
import glob, os, sys
sys.path.insert(0,'.'); import sigdet as SD
from obspy import UTCDateTime
LOOK=int(round(120/SD.DT))
ev={}
for st in ('H01W','H08S'):
    d=pd.read_csv(f'bc/out/eq_{st}_events.csv'); d=d[d.status=='ok']
    for _,r in d.iterrows(): ev[f'{st}1_{r.evid}']=r
B=[];K=[]
for fn in sorted(glob.glob('scores/*.npz')):
    k=os.path.basename(fn)[:-4]; z=np.load(fn); st=k[:4]; r=ev[k]; t=z['t']
    tev=UTCDateTime(r.t_pred)-UTCDateTime(str(z['start']))
    A={'L_d0':z['d0'],'S_d2':z['s_d2'],'S_d1':z['s_d1'],'L_d1':z['d1']}
    bad=z['gap'].astype(bool)
    for v in A.values(): bad|=~np.isfinite(v)
    excl=(t>=tev-120)&(t<=tev+420)
    for i in range(0,len(t)-LOOK,LOOK):
        sl=slice(i,i+LOOK)
        if excl[sl].any() or bad[sl].any(): continue
        B.append(dict(st=st,**{s:float(np.max(v[sl])) for s,v in A.items()}))
    look=(t>=tev-40)&(t<=tev+80)
    if look.sum()>200 and not bad[look].any():
        K.append(dict(st=st,rec=k,evid=r.evid,snr_db=r.snr_db,**{s:float(np.max(v[look])) for s,v in A.items()}))
B=pd.DataFrame(B); K=pd.DataFrame(K)
def thr(st,s,q): return np.quantile(B[B.st==st][s],q)
res=[]
for st,g in K.groupby('st'):
    d0=g.L_d0>thr(st,'L_d0',0.95)
    orS=(g.L_d0>thr(st,'L_d0',0.975))|(g.S_d2>thr(st,'S_d2',0.975))
    orL=(g.L_d0>thr(st,'L_d0',0.975))|(g.L_d1>thr(st,'L_d1',0.975))
    K.loc[g.index,'det_d0']=d0; K.loc[g.index,'det_orS']=orS; K.loc[g.index,'det_orL']=orL
    # null check on background
    gb=B[B.st==st]
    fa=dict(d0=(gb.L_d0>thr(st,'L_d0',0.95)).mean(), orS=((gb.L_d0>thr(st,'L_d0',0.975))|(gb.S_d2>thr(st,'S_d2',0.975))).mean(),
            orL=((gb.L_d0>thr(st,'L_d0',0.975))|(gb.L_d1>thr(st,'L_d1',0.975))).mean())
    print(st,'background false-alarm per look',{k:round(v,3) for k,v in fa.items()})
K['strength']=pd.cut(K.snr_db,[-1,10,15,20,99],labels=['<10','10-15','15-20','>20'])
tab=K.groupby(['st','strength'])[['det_d0','det_orS','det_orL']].agg(['mean','size'])
print(tab.round(2).to_string())
for st,g in K.groupby('st'):
    for c in ('det_orS','det_orL'):
        a=((~g.det_d0)&g[c]).sum(); b=(g.det_d0&~g[c]).sum()
        print(st,c,'new only',a,'lost',b,'McNemar p',round(binomtest(a,a+b).pvalue,4) if a+b else 1)
w=K[K.snr_db<10]
for st,g in w.groupby('st'):
    for c in ('det_d0','det_orS','det_orL'):
        print(st,'weak <10 dB',c,f'{int(g[c].sum())}/{len(g)}','binomial p vs 0.05:',round(binomtest(int(g[c].sum()),len(g),0.05,alternative="greater").pvalue,4))
K.to_csv('known_events_control.csv',index=False); B.to_csv('background_looks_eq_v2.csv',index=False)
# two-station known-time test: events recorded at both stations
both=K.pivot_table(index='evid',columns='st',values=['L_d0','S_d2']).dropna()
print('events at both stations:',len(both))
def p_emp(st,s,x): v=np.sort(B[B.st==st][s].values); return (len(v)-np.searchsorted(v,x)+1)/(len(v)+1)
rows=[]
for evid,r in both.iterrows():
    p1=min(p_emp('H01W','L_d0',r[('L_d0','H01W')]),p_emp('H01W','S_d2',r[('S_d2','H01W')]))*2
    p2=min(p_emp('H08S','L_d0',r[('L_d0','H08S')]),p_emp('H08S','S_d2',r[('S_d2','H08S')]))*2
    rows.append(dict(evid=evid,p1=min(p1,1),p2=min(p2,1)))
P=pd.DataFrame(rows); from scipy.stats import chi2
P['fisher']=chi2.sf(-2*np.log(P.p1*P.p2),4)
snr=K.pivot_table(index='evid',columns='st',values='snr_db'); P=P.join(snr,on='evid')
P['weak_both']=(P.H01W<15)&(P.H08S<15)
print(P.groupby('weak_both').apply(lambda g: pd.Series({'n':len(g),'H01W p<.05':(g.p1<.05).mean(),'H08S p<.05':(g.p2<.05).mean(),'either':((g.p1<.025)|(g.p2<.025)).mean(),'two-station Fisher p<.05':(g.fisher<.05).mean()})).round(2))
P.to_csv('two_station_known.csv',index=False)
