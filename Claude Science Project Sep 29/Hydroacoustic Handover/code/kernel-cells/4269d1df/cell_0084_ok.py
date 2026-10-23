print(RC[(RC.model=='mean')&(RC.option.isin(['none','populated']))&(RC.variant.isin(['T_core','C_core']))][['D','variant','option','LLR','sd_total','ESS']].round(2).to_string())
TB=np.arange(1394236800.0-3600,1394236800.0+5400+1,30.0); tc=(TB[:-1]+TB[1:])/2
dbins=np.arange(-300,601,10); dc=(dbins[:-1]+dbins[1:])/2
def wq(x,w,q): o=np.argsort(x); c=np.cumsum(w[o])/w.sum(); return [float(x[o][np.searchsorted(c,qq)]) for qq in q]
import datetime as dt
fmt=lambda u: dt.datetime.utcfromtimestamp(u).strftime('%H:%M:%S')
for D in ['D0','D2','D3']:
    for v in VARS[1:]:
        pc=P[(D,v)]; th=pc['thist'].sum(0); di=pc['din'].sum(0)
        tq=[fmt(x) for x in wq(tc,th,[0.05,0.5,0.95])]; dq=wq(dc,di,[0.05,0.5,0.95])
        w=pc['sum']; print(D,v,'t_impact 5/50/95',tq,'range beyond arc km (neg = outside arc)',[round(x) for x in dq],
              'lat/lon mean',round(float((pc['lat_mean']*w).sum()/w.sum()),2),round(float((pc['lon_mean']*w).sum()/w.sum()),2),'parents99 sum',int(pc['parents99'].sum()),
              {s:round(float(w[pc['strata']==s].sum()/w.sum()),4) for s in strata_names})
