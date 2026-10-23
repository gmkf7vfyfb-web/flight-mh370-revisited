print(a.keys())
alat=np.array(a['lat_mid']); alon=np.array(a[[k for k in a if 'lon' in k][0]])
ok=np.isfinite(alon); alat,alon=alat[ok],alon[ok]
fl=np.linspace(alat.min(),alat.max(),800); fo=np.interp(fl,alat,alon)
def arc_dist(la,lo):
    d=G.inv(np.full_like(fo,lo),np.full_like(fl,la),fo,fl)[2]/1000; i=np.argmin(d); return d[i], fl[i]
for _,e in ev.iterrows():
    d,L=arc_dist(e.lat_deg,e.lon_deg)
    tc=time_cls(e.origin_s_after_T0)
    lab=e.label if isinstance(e.label,str) else f"#{e['index']}"
    known = {'icequake':'Royer class: icequake','earthquake':'Royer class: earthquake'}.get(e.event_class,'')
    if lab in ('C1','C2','C3','C4'): known='Same H01W arrival (01:34:29-01:34:33) as the CMST 2014 event; four alternative Royer solutions'
    add(id='R-'+lab, group='Published: Royer 2016 OHASISBIO located events', label=f"Royer {lab} ({e.event_class})", receivers=f"{e.n_hydrophones} hydrophones (OHASISBIO + H01W)",
        times=e.origin_time_utc, bearing='', implied_lat=e.lat_deg, implied_lon=e.lon_deg, implied_impact=e.origin_time_utc, time_test=tc,
        location_test=('inside prior' if d<60 else f"{d:.0f} km from the 7th arc (nearest arc point {L:.1f} S)"), prior_mass_1deg=np.nan,
        bearing_test='', energy_test='not needed (fails location)' if d>=60 else 'not computed', known_event=known)
# CMST 2014 event
add(id='CMST-0134', group='Published: Curtin CMST 2014', label='Curtin CMST event (Perth Canyon ~01:33:42; H01W 01:34:29-01:34:33)', receivers='IMOS Perth Canyon, H01W (and Royer OHASISBIO)',
    times='01:33:42 (Perth Canyon, CMST Fig.)', bearing='north-west (CMST maps)', implied_lat=np.nan, implied_lon=np.nan, implied_impact='Royer C1 00:33:43 / C2 00:57:32 / C3 00:57:34 / C4 00:59:55',
    time_test='inside (C1-C4 origin times)', location_test='all four Royer solutions >1,000 km from the arc; CMST bearing points north-west, away from the arc', prior_mass_1deg=np.nan,
    bearing_test='', energy_test='not needed (fails location)', known_event='Royer C1-C4; CMST judged it not consistent with the arc')
for tt in ['23:57','00:11']:
    add(id='K19-'+tt, group='Published: Kadri 2019 (H08S)', label=f'Kadri 2019 Table 3 signal of interest {tt} UTC', receivers='H08S', times=tt, bearing='', implied_lat=np.nan, implied_lon=np.nan,
        implied_impact='before arrival could start', time_test='impossible (arrives at H08S before any impact after 00:19:29 could be heard there)', location_test='', prior_mass_1deg=np.nan,
        bearing_test='', energy_test='not needed (fails time)', known_event='')
pb=pd.read_csv(H+'searches_run_j/named/poster_boxes.csv')
for _,r in pb[pb.box.str.startswith('poster')].iterrows():
    kn='Contains Royer event B H01W pick bar 00:36:07-00:36:34 (event B: 35.22 S 99.92 E, 00:21:30, 493 km off arc)' if r.box.endswith('4') else ''
    add(id='KP-'+r.box[-5:].replace(' ',''), group='Published: Kadri SnT 2025 poster panel (a)', label=r.box, receivers='H01W', times=f"{r.start}-{r.end}", bearing='',
        implied_lat=np.nan, implied_lon=np.nan, implied_impact='', time_test=('impossible (ends %.1f min before the earliest arc arrival)'%r.minutes_before_earliest) if r.ends_before_earliest_arc_arrival else 'marginal (arc point near 28-30 S only)',
        location_test='', prior_mass_1deg=np.nan, bearing_test='', energy_test='', known_event=kn)
R=pd.DataFrame(reg); print(R[R.group.str.contains('Royer|CMST|2019|poster')][['id','times','implied_lat','implied_lon','time_test','location_test','known_event']].to_string())