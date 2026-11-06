import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); import pmap
B=pd.read_csv('joint_background.csv'); P=pmap.PMap(B,'rnd')
d=pd.read_csv('injections_rnd_v3.csv')
for st in ('H01W','H08S'):
    m=d.st==st; d.loc[m,'COMB']=P.fisher(st,{s:d.loc[m,s].values for s in pmap.COMB})
DET=pmap.STATS+['COMB']
LEV={'known 50%':0.5,'known 20%':0.2,'known 10%':0.1,'known 5%':0.05,'30 min 50%':0.5/15,'30 min 20%':0.2/15,'30 min 5%':0.05/15,'blind 1/day':1/720}
T={(st,s,l):P.thr(st,s,a) for st in ('H01W','H08S') for s in DET for l,a in LEV.items()}
n20=d[d.snr==-20]
print('null exceedance at -20 dB (per look; nominal in brackets)')
print(pd.DataFrame({s:{f'{l} ({a:.4f})':round(np.mean([r[s]>T[(r.st,s,l)] for _,r in n20.iterrows()]),4) for l,a in LEV.items()} for s in DET}).to_string())
rows=[]
for (st,cls,snr),g in d.groupby(['st','cls','snr']):
    for s in DET:
        for l in LEV: rows.append(dict(st=st,cls=cls,snr=snr,det=s,level=l,pd=(g[s]>T[(st,s,l)]).mean(),n=len(g)))
pdt=pd.DataFrame(rows); pdt.to_csv('pd_v3.csv',index=False)
def snr50(g):
    g=g.sort_values('snr'); x=g.snr.values; y=g.pd.values; i=np.where(y>=0.5)[0]
    if len(i)==0: return np.nan
    i=i[0]; return x[0] if i==0 else x[i-1]+(0.5-y[i-1])*(x[i]-x[i-1])/(y[i]-y[i-1])
s50=pdt.groupby(['st','cls','level','det']).apply(snr50).unstack('det')[DET]
s50.to_csv('snr50_v3.csv')
pd.set_option('display.width',250)
for cls in ['dive','ditch','realquake','zcall','airgun','ship','ice']:
    print('\n',cls); print(s50.xs(cls,level='cls').reindex(list(LEV),level='level').round(1).to_string())
