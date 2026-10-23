
T0=1394236800.0
Lm=L[L.in_strip|L.CX100|L.HX100].copy()
Lm['vh']=np.hypot(Lm.velocity_east_mps,Lm.velocity_north_mps); Lm['vd']=-Lm.velocity_up_mps
Lm['t_utc_min']=Lm.t_impact_s/60.0   # minutes after 00:00 UTC
Lm['w0']=Lm.weight/Lm.seed_wsum
ll=Lm['loglik:r600/no-offset'].astype(float)
Lm['w2']=Lm.w0*np.exp(ll-np.nanmax(ll))
del L; import gc; gc.collect()
def wq(x,w,q=(.05,.5,.95)):
    o=np.argsort(x); x=np.asarray(x)[o]; w=np.asarray(w)[o]; c=np.cumsum(w); c/=c[-1]; return [float(np.interp(qq,c,x)) for qq in q]
print(len(Lm))
for st,g in Lm.groupby('stratum'):
    w=g.w0.values
    print(st,len(g),'vh',np.round(wq(g.vh,w)),'vd',np.round(wq(g.vd,w)),'t',[f'{int(m//60):02d}:{int(m%60):02d}' for m in wq(g.t_utc_min,w)],
          'debris',{int(k):round(float(v),3) for k,v in g.groupby('latent:debris_class').w0.sum().div(w.sum()).items()},
          'pI/pB/pF',np.round([np.average(g['latent:breakup_p_intact'],weights=w),np.average(g['latent:breakup_p_broken'],weights=w),np.average(g['latent:breakup_p_fragmented'],weights=w)],3))
print(Lm['latent:debris_class'].value_counts().to_dict(), Lm.family.value_counts().to_dict())
