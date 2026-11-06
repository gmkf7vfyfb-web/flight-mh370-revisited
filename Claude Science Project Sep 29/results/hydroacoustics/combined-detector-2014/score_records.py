import sys, glob, os, numpy as np, pandas as pd
sys.path.insert(0,'.'); import sigdet as SD
from obspy import read
from multiprocessing import Pool
RD=os.environ.get('SIG_RD','/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records')
OUT=os.environ.get('SIG_OUT','scores'); os.makedirs(OUT,exist_ok=True)
SCALE={'H01W':1839.18,'H08S':1845.14}
WT=SD.whale_templates()
def load(fn, st):
    s=read(fn); s.merge(fill_value=0); tr=s[0]
    x=tr.data.astype(float)/SCALE[st]
    nz=x!=0; x[nz]-=x[nz].mean()
    return tr.stats.starttime, x
def run(fn):
    name=os.path.basename(fn)[:-6]; st=name[:4]
    o=f'{OUT}/{name}.npz'
    if os.path.exists(o): return name
    try:
        t0,x=load(fn,st)
        if len(x)<SD.FS*1500: return name+':short'
        t,P,N,S,Ss=SD.all_scores(x,wt=WT)
        C=SD.combine(S); Cs=SD.combine(Ss)
        gap=(P[SD.FB].sum(0)<=0)|(np.abs(x[(t*SD.FS).astype(int)])==0)
        np.savez_compressed(o,t=t,start=str(t0),gap=gap,Nmed=np.median(N,axis=1),
            **{k:v.astype(np.float32) for k,v in C.items() if k!='winner' and not k.startswith('c_')},winner=C['winner'].astype(np.int8),
            **{'cls_'+k:SD.lag_max(v,40).astype(np.float32) for k,v in S.items() if k!='d0'},
            **{'s_'+k:v.astype(np.float32) for k,v in Cs.items() if k not in ('winner','d0') and not k.startswith('c_')},s_winner=Cs['winner'].astype(np.int8),
            **{'scls_'+k:SD.lag_max(v,40).astype(np.float32) for k,v in Ss.items() if k!='d0'})
        return name
    except Exception as e:
        return name+':ERR '+str(e)[:100]
if __name__=='__main__':
    fs=sorted(glob.glob(RD+'/*.mseed'))
    with Pool(16) as p: res=p.map(run,fs,chunksize=4)
    bad=[r for r in res if ':' in r]; print(len(res),'bad',len(bad)); print(bad[:10])
