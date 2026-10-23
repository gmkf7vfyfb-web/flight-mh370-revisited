recv=['H01W','H08S','3315','3376','3274','3275','3250']
kadri_cov={'H01W':[(hms('00:27:00'),hms('00:57:00'))],'H08S':cov['H08S']}
# Kadri panel extents: use digitised panel extents
s=pd.read_csv(RK+'ranked_singles.csv')
t1=pd.read_csv(H+'searches_run_j/named/table1_verdicts.csv')
# candidate list
C=[]
for _,r in s.iterrows(): C.append(dict(rx=str(r.rx), t=hms(r.time_utc), src='module search '+str(r.det)+' p='+f"{r.p:.3f}", cid=f"S{int(r.rank_lnLR)}"))
for _,r in t1.iterrows(): C.append(dict(rx='H01W', t=hms(r.time_utc), src=f"Kadri Table 1 {r.time_utc} ({r.bearing_deg} deg)", cid='K'+r.time_utc))
C.append(dict(rx='H01W',t=hms('00:52:03'),src='Kadri text time',cid='Ktext'));C.append(dict(rx='H01W',t=hms('00:54:30'),src='Kadri caption time',cid='Kcap'))
C=pd.DataFrame(C)
def covered(r,t):
    spans = kadri_cov.get(r,[]) if r in ('H01W','H08S') else held[r]
    return any(a<=t<=b for a,b in spans)
rows=[]
for _,e in ev.iterrows():
    t0=e.origin_s_after_T0
    ea=arr[(arr['index']==e['index'])&arr.arrival_utc.notna()]
    spd=ea.implied_speed_km_s.median() if len(ea) else 1.482
    for r in recv:
        la,lo=rx[r]; d=G.inv(e.lon_deg,e.lat_deg,lo,la)[2]/1000
        if r=='H01W' and len(ea[ea.station.str.startswith('H01W')]):
            tp=ea[ea.station.str.startswith('H01W')].t_arr.mean(); basis='Royer pick'
            sig=max(3.0, 2)  # pick
        else:
            tp=t0+d/spd; basis=f'geodesic/{spd:.4f}'
            sig=np.hypot(e.err_time_s if e.err_time_s<99 else 60, d/spd*0.006/1.48)
        tol=max(20.0, 3*sig)
        cand=C[(C.rx==r)&((C.t-tp).abs()<=tol+(16 if r=='H01W' else 0))]
        rows.append(dict(event=int(e['index']),label=e.label if isinstance(e.label,str) else '',cls=e.event_class,lat=e.lat_deg,lon=e.lon_deg,origin=e.origin_time_utc,
                         rx=r,range_km=round(d),pred=fmt(tp),basis=basis,tol_s=round(tol,1),data_held=covered(r,tp),
                         matches='; '.join(f"{fmt(c.t)} {c.src} (dt {c.t-tp:+.0f}s)" for _,c in cand.iterrows())))
X=pd.DataFrame(rows)
hit=X[(X.matches!='')]
print(hit[['event','label','cls','rx','pred','basis','tol_s','matches']].to_string())
print(X[X.data_held][['event','label','cls','rx','pred','matches']].to_string())