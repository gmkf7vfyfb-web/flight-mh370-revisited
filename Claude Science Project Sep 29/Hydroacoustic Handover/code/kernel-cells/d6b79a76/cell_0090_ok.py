def hq(h,edges,qs=(0.05,0.5,0.95)):
    n=len(edges)-1; hh=h[:n]; c=np.cumsum(hh)/hh.sum(); return [float(edges[min(np.searchsorted(c,q),n-1)]/60+0.5) for q in qs]
TQ=[]
for pool,keys in (('main',HK),('joined',[f'D{d} joined V2' for d in range(5)])):
    for k in keys:
        for reg in ['all','strip','X100','X200','H200']:
            row={'pool':pool,'key':k.replace(' total q=0.333 (C2 silent)',''),'region':reg}
            for which,ed in (('t',W.TB),('fo',W.FB),('aloft',W.AB)):
                h,_=A.pooled_hist(seeds,pool,k,reg,which)
                if h is None: continue
                q=hq(h,ed); row[f'{which}_q05_q50_q95_min']='/'.join(f'{x:.1f}' for x in q)
                if which=='fo': row['no_flameout_share']=float(h[-1]/h.sum())
                if which=='aloft': row['powered_at_impact_share']=float(h[-1]/h.sum()); row['aloft_ge60_share']=float(h[-2]/h.sum())
            TQ.append(row)
tq=pd.DataFrame(TQ); print(tq[tq.region.isin(['all','strip','X200'])].to_string())