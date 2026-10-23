searched={r:sum(b-a for a,b in cov[r]) for r in cov}
ncand={r:(C.rx==r).sum() for r in recv}
print(searched, ncand)
rows=[]
for _,r in X.iterrows():
    if not r.matches: continue
    for mtxt in r.matches.split('; '):
        tm=mtxt.split(' ')[0]; dt=float(mtxt.split('(dt ')[1].rstrip('s)'))
        rate=ncand[r.rx]/searched[r.rx]
        lam=rate*2*max(abs(dt),2.0)
        rows.append(dict(event=r.event,label=r.label,cls=r.cls,origin=r.origin,lat=r.lat,lon=r.lon,rx=r.rx,predicted=r.pred,basis=r.basis,tol_s=r.tol_s,candidate=mtxt.split(' (dt')[0],dt_s=dt,chance_expect=round(lam,3)))
M=pd.DataFrame(rows)
# keep best (smallest |dt|) per event x rx x candidate source type
M['abs']=M.dt_s.abs()
best=M.sort_values('abs').groupby(['event','rx']).head(1).sort_values(['event','rx'])
print(best[['event','label','cls','rx','predicted','candidate','dt_s','chance_expect']].to_string())