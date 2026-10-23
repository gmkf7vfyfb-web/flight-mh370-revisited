topidx=set()
for c in CH:
    if 'joined' in c['key']: continue
    topidx|=set(c['_top'].tolist())
# also rows carrying 99% of sum wL for headline D0/D2/D3/D4 T1.0 C1.0
for d in (0,1,2,3,4,5):
    for vn in ('T1.0','C1.0','T0.5','C0.5'):
        lw=(M[f'lm|D{d} total q=0.333 (C2 silent)']+M['lnL|'+vn]).values; fin=np.isfinite(lw); w=np.where(fin,np.exp(lw-lw[fin].max()),0)
        o=np.argsort(-w); n=np.searchsorted(np.cumsum(w[o])/w.sum(),0.99)+1; topidx|=set(o[:n].tolist())
topidx=np.array(sorted(topidx)); T=M.iloc[topidx]
need=T.groupby(['stratum','seed']).size(); print(len(topidx), len(need), need.groupby(level=0).size().to_dict())