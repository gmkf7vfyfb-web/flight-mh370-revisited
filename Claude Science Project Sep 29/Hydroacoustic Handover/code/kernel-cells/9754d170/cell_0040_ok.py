
BANDS=[5.0,6.3,8.0,10.0,12.5,16.0,20.0,25.0,31.5,40.0,50.0,63.0]
def obs_bands(st):
    o=obs[obs.station==st]; out={}
    for fc in BANDS:
        m=(o.f_hz>=fc*2**(-1/6))&(o.f_hz<fc*2**(1/6))
        if m.sum()>=2: out[fc]=10*np.log10(np.mean(10**(o.tl_db[m]/10)))  # power mean of TL? 
    return out
def stats(fb, r):
    x=np.log2(np.array(fb)); r=np.array(r)
    A=np.vstack([np.ones_like(x),x-x.mean()]).T
    c,res,_,_=np.linalg.lstsq(A,r,rcond=None)
    det=r-A@c; n=len(r)
    se=np.sqrt(det@det/(n-2)/np.sum((x-x.mean())**2)) if n>2 else np.nan
    return dict(n=n,span=(min(fb),max(fb)),level=float(np.median(r)),mean=float(r.mean()),slope=float(c[1]),slope_se=float(se),shape_rms=float(np.sqrt(np.mean(det**2))),rms=float(np.sqrt(np.mean(r**2))))
def grade(v,p,q): 
    v=abs(v); return 'PASS' if v<=p else ('PARTIAL' if v<=q else 'FAIL')
def verdict(s,shape=(3,5)):
    g=[grade(s['level'],3,6),grade(s['slope'],1.5,3),grade(s['shape_rms'],*shape)]
    return g, ('FAIL' if 'FAIL' in g else ('PASS' if all(x=='PASS' for x in g) else 'PARTIAL'))
ob={st:obs_bands(st) for st in ['H01W','H08S']}
for st in ob: print(st,{k:round(v,1) for k,v in ob[st].items()})
res={}
for zs in [9.0,10.0,12.0]:
    for st in ['H01W','H08S']:
        fb=[f for f in ob[st] if f in p.index]
        r=[ob[st][f]-p.loc[f,(st,zs)] for f in fb]
        s=stats(fb,r); res[(st,zs)]=(fb,r)
        print(zs,st,{k:(round(v,2) if isinstance(v,float) else v) for k,v in s.items()},verdict(s))
