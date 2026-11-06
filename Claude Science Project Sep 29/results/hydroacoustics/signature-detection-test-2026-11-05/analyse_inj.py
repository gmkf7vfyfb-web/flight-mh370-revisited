import pandas as pd, numpy as np, sys
tag=sys.argv[1]; thfile=sys.argv[2]
d=pd.read_csv(f'injections_{tag}.csv'); th=pd.read_csv(thfile)
T={(r.st,r.stat,r.level):r.thr for r in th.itertuples()}
DET=['L_d0','L_d1','L_d2','S_d1','S_d2']
LEV=['known_time_0.05','window30min_0.05','blind_1_per_day']
# null check: rows at -20 dB
n20=d[d.snr==-20]
print('exceedance at -20 dB (nominal 0.05 / 0.0033 / 0.0014):')
print(pd.DataFrame({det:[ (n20.apply(lambda r: r[det]>T[(r.st,det,l)],axis=1)).mean().round(4) for l in LEV] for det in DET},index=LEV))
rows=[]
for (st,cls,snr),g in d.groupby(['st','cls','snr']):
    for det in DET:
        for l in LEV:
            rows.append(dict(st=st,cls=cls,snr=snr,det=det,level=l,pd=(g[det]>T[(st,det,l)]).mean()))
pdt=pd.DataFrame(rows); pdt.to_csv(f'pd_{tag}.csv',index=False)
def snr50(g):
    g=g.sort_values('snr'); x=g.snr.values; y=g.pd.values
    i=np.where(y>=0.5)[0]
    if len(i)==0: return np.nan
    i=i[0]
    if i==0: return x[0]
    return x[i-1]+(0.5-y[i-1])*(x[i]-x[i-1])/(y[i]-y[i-1])
s50=pdt.groupby(['st','level','cls','det']).apply(snr50).unstack('det')[DET]
s50.to_csv(f'snr50_{tag}.csv')
pd.set_option('display.width',200)
for l in LEV:
    print('\nSNR at 50% detection,', l); print(s50.xs(l,level='level').round(1).to_string())
# impact labelling: winner index 0,1 = dive/ditch
for mode in ('L','S'):
    d[f'{mode}_imp']=d[f'{mode}_win']<=1
lab=d[d.snr.isin([-5,0,5,10])].groupby(['st','cls','snr'])[['L_imp','S_imp']].mean().unstack('snr')
print('\nfraction labelled impact-like at peak (L mode / S mode):'); print(lab.round(2).to_string())
