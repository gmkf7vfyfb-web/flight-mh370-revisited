import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); import pmap
B=pd.read_csv('joint_background.csv'); P=pmap.PMap(B,'rnd'); G=pmap.PMap(B,'gauss')
d=pd.read_csv('injections_rnd_v3.csv')
for st in ('H01W','H08S'):
    m=d.st==st; d.loc[m,'COMB']=P.fisher(st,{s:d.loc[m,s].values for s in pmap.COMB})
DET=pmap.STATS+['COMB']; NL=[1,2,5,15,50,150,720]
def snr50(g,thr,s):
    x=np.sort(g.snr.unique()); y=np.array([(g[g.snr==v][s]>thr).mean() for v in x]); i=np.where(y>=0.5)[0]
    if len(i)==0: return np.nan
    i=i[0]; return x[0] if i==0 else x[i-1]+(0.5-y[i-1])*(x[i]-x[i-1])/(y[i]-y[i-1])
rows=[]
for st in ('H01W','H08S'):
    for cls in ('dive','ditch','realquake'):
        g=d[(d.st==st)&(d.cls==cls)]
        for s in DET:
            for n in NL:
                a=0.05/n
                rows.append(dict(st=st,cls=cls,det=s,looks=n,thr_real=P.thr(st,s,a),thr_gauss=G.thr(st,s,a),thr_real50=P.thr(st,s,0.5),thr_gauss50=G.thr(st,s,0.5),snr50=snr50(g,P.thr(st,s,a),s)))
L=pd.DataFrame(rows); L.to_csv('snr_vs_looks.csv',index=False)
R=[]
for st in ('H01W','H08S'):
    for cls in ('dive','ditch','realquake'):
        for snr in (-10.0,-5.0,0.0):
            g=d[(d.st==st)&(d.cls==cls)&(d.snr==snr)]
            for s in DET:
                for a in (0.01,0.02,0.05,0.1,0.2,0.3,0.5):
                    R.append(dict(st=st,cls=cls,snr=snr,det=s,pfa=a,pd=(g[s]>P.thr(st,s,a)).mean()))
R=pd.DataFrame(R); R.to_csv('roc_known_time.csv',index=False)
pd.set_option('display.width',200)
print(L[L.cls=='dive'].pivot_table(index=['st','det'],columns='looks',values='snr50').round(1))
print(L[L.cls=='realquake'].pivot_table(index=['st','det'],columns='looks',values='snr50').round(1))
print(R[(R.cls=='dive')&(R.snr==-5)].pivot_table(index=['st','det'],columns='pfa',values='pd').round(2))
