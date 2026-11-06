import pandas as pd, numpy as np, sys
# empirical tail probability against a background distribution, then min-p combination calibrated on background
def tailp(bgv, x):
    s=np.sort(bgv); n=len(s)
    return (n - np.searchsorted(s, x, side='left') + 1)/(n+1)
def add_combo(df, bg, pairs):
    for name,(a,b) in pairs.items():
        for st in df.st.unique():
            m=df.st==st; g=bg[bg.st==st]
            df.loc[m,name]=-np.log10(np.minimum(tailp(g[a].values,df.loc[m,a].values),tailp(g[b].values,df.loc[m,b].values)))
    return df
PAIRS={'C_d0_or_Sd1':('L_d0','S_d1'),'C_d0_or_Sd2':('L_d0','S_d2'),'C_d0_or_Ld1':('L_d0','L_d1')}
if __name__=='__main__':
    bg=pd.read_csv('background_looks_rnd.csv'); d=pd.read_csv('injections_rnd.csv')
    bg=add_combo(bg.copy(),bg,PAIRS); d=add_combo(d,bg,PAIRS)
    Q={'known_time_0.05':0.95,'window30min_0.05':1-0.05/15,'blind_1_per_day':1-1/720}
    T={(st,c,l):np.quantile(g[c],q) for st,g in bg.groupby('st') for c in list(PAIRS)+['L_d0'] for l,q in Q.items()}
    rows=[]
    for (st,cls,snr),g in d.groupby(['st','cls','snr']):
        for c in list(PAIRS)+['L_d0']:
            for l in Q: rows.append(dict(st=st,cls=cls,snr=snr,det=c,level=l,pd=(g[c]>T[(st,c,l)]).mean()))
    p=pd.DataFrame(rows); p.to_csv('pd_combo_rnd.csv',index=False)
    def snr50(g):
        g=g.sort_values('snr'); x=g.snr.values; y=g.pd.values; i=np.where(y>=0.5)[0]
        if len(i)==0: return np.nan
        i=i[0]; return x[0] if i==0 else x[i-1]+(0.5-y[i-1])*(x[i]-x[i-1])/(y[i]-y[i-1])
    s=p.groupby(['st','level','cls','det']).apply(snr50).unstack('det'); s.to_csv('snr50_combo_rnd.csv')
    pd.set_option('display.width',200)
    print(s[s.index.get_level_values('cls').isin(['dive','ditch','realquake','implosion'])].round(1).to_string())
    n20=d[d.snr==-20]; print('null exceed:',{c:{l:round((n20.apply(lambda r:r[c]>T[(r.st,c,l)],axis=1)).mean(),4) for l in Q} for c in PAIRS})
