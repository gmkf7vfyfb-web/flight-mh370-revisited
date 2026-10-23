def royer_flag(r,t):
    t=hms(t); g=best[(best.rx==str(r))]
    out=[]
    for _,b in g.iterrows():
        if abs(hms(b.candidate.split(' ')[0])-t)<=2 and b.chance_expect<0.5:
            out.append(f"Royer event {b.label or '#'+str(b.event)} ({b.cls}) predicted {b.predicted}, dt {b.dt_s:+.0f} s")
    if str(r)=='H01W' and abs(t-hms('00:52:03'))<=3: out.append('Royer event A pick bar (icequake)')
    if str(r)=='H01W' and abs(t-hms('00:54:30'))<=3: out.append('Royer event 5 arrow (uncertain, 49.8 S 133.1 E)')
    return '; '.join(out)
# feasible distinct pairs
Fd=F.copy(); Fd['key']=Fd.rx_a+Fd.t_a+Fd.rx_b+Fd.t_b
Fd=Fd.sort_values('rank_lnLR').drop_duplicates('key')
for _,r in Fd.iterrows():
    kf='; '.join(x for x in [royer_flag(r.rx_a,r.t_a), royer_flag(r.rx_b,r.t_b)] if x)
    add(id=f"MP-{int(r.rank_lnLR)}", group='Module search: two-site sets passing time, place and energy screens', label=f"pair rank {int(r.rank_lnLR)} (ln LR {r.lnLR:.2f}); permutation p {r.p_perm}",
        receivers=f"{r.rx_a} x {r.rx_b}", times=f"{r.t_a} / {r.t_b} (p {r.p_a:.3f} / {r.p_b:.3f})", bearing=('H01W only, no Kadri bearing' if 'H01W' in (r.rx_a+r.rx_b) else 'none (IMOS has no bearing)'),
        implied_lat=round(r.locus_lat,2), implied_lon=round(r.locus_lon,2), implied_impact=r.implied_impact_utc, time_test=r.time_cls, location_test=r.loc_cls, prior_mass_1deg=round(r.loc_mass,4),
        bearing_test='', energy_test=f"{r.eta_min_xF35A:.1f}x F-35A at the 99th-percentile energy ({r.eta_min:.2g})", known_event=kf)
for _,r in Tc[kt].head(1).iterrows():
    add(id=f"MT-{int(r.rank_lnLR)}", group='Module search: three-site set passing all screens', label=f"triple rank {int(r.rank_lnLR)} (ln LR {r.lnLR:.2f})", receivers=r.rxs, times=f"{r.times} (p {r.ps})", bearing='',
        implied_lat=round(r.locus_lat,2), implied_lon=round(r.locus_lon,2), implied_impact=r.implied_impact_utc, time_test='inside', location_test='inside prior', prior_mass_1deg=round(locm(r.locus_lat),4),
        bearing_test='', energy_test=f"{r.eta_min_xF35A:.1f}x F-35A at the 99th-percentile energy", known_event='')
# the two headline pairs from last night
for rk in [1, 104]:
    r=Pc[Pc.rank_lnLR==rk].iloc[0]
    kf='; '.join(x for x in [royer_flag(r.rx_a,r.t_a), royer_flag(r.rx_b,r.t_b)] if x)
    sh='; '.join(f"{rx} {t} is {d:+.2f} s from an airgun shot" for rx,t,d in [(r.rx_a,r.t_a,r.dtshot_a),(r.rx_b,r.t_b,r.dtshot_b)] if rx=='H08S')
    add(id=f"MP-{rk}", group='Module search: headline pairs from the overnight run', label=('top-ranked pair' if rk==1 else "'strongest two-site pair' (row G)"), receivers=f"{r.rx_a} x {r.rx_b}",
        times=f"{r.t_a} / {r.t_b}", bearing='', implied_lat=round(r.locus_lat,2), implied_lon=round(r.locus_lon,2), implied_impact=r.implied_impact_utc, time_test=r.time_cls, location_test=r.loc_cls,
        prior_mass_1deg=round(r.loc_mass,4), bearing_test=('Kadri bearing 306.18/57 deg vs locus 268.9 deg: inconsistent' if rk==104 else ''), energy_test=f"{r.eta_min_xF35A:.0f}x F-35A at the 99th-percentile energy ({r.eta_min:.2g})",
        known_event='; '.join(x for x in [kf, sh] if x))
R=pd.DataFrame(reg)
def verdict(r):
    tt=str(r.time_test); lt=str(r.location_test); et=str(r.energy_test); ke=str(r.known_event)
    if 'airgun' in ke: return 'NOT MH370: airgun artefact'
    if tt.startswith('impossible'): return 'NOT FEASIBLE: time'
    if ('km from the 7th arc' in lt) or ('misses the arc' in lt) or lt.startswith('outside') or ('>1,000 km' in lt): return 'NOT FEASIBLE: location'
    if 'Royer class' in ke or 'Royer event' in ke or 'Royer C1-C4' in ke or 'Same H01W arrival' in ke or 'pick bar' in ke or 'arrow' in ke: return 'LIKELY KNOWN OTHER EVENT'
    if 'x F-35A' in et:
        v=float(et.split('x')[0])
        if v>100: return 'NOT FEASIBLE: energy'
        if v>10: return 'STRAINED: energy'
    if 'outside 99%' in tt: return 'WEAK: time outside 99% of prior'
    if 'edge of prior' in lt: return 'WEAK: location at north edge of prior'
    if 'marginal' in tt: return 'MARGINAL: time'
    return 'FEASIBLE (not supported above chance)'
R['verdict']=R.apply(verdict,axis=1)
print(R.groupby('group').verdict.value_counts().to_string())