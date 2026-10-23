
Lm['t_utc_min']=Lm.t_utc_min.fillna(30.0); Lm['t_missing']=Lm.t_impact_s.isna()
def hm(m): return f'{int(m//60):02d}:{int(m%60):02d}'
summ=[]
for st,g in Lm.groupby('stratum'):
    w=g.w0.values
    dc={int(k):round(float(v),3) for k,v in g.groupby('latent:debris_class').w0.sum().div(w.sum()).items()}
    summ.append(dict(stratum=st,rows=len(g),ess=round(w.sum()**2/(w**2).sum()),vh=np.round(wq(g.vh,w)).tolist(),vd=np.round(wq(g.vd,w)).tolist(),
        t=[hm(m) for m in wq(g.t_utc_min,w)] if not g.t_missing.all() else 'absent',debris=dc,
        pIBF=np.round([np.average(g['latent:breakup_p_intact'],weights=w),np.average(g['latent:breakup_p_broken'],weights=w),np.average(g['latent:breakup_p_fragmented'],weights=w)],3).tolist()))
for s_ in summ: print(s_)
