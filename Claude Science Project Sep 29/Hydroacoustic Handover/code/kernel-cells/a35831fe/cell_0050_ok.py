def locm(L): return float(fE(L,mass)) if np.isfinite(L) else np.nan
def in99lat(L): return (-38.97<=L<=-25.01)
reg=[]
def add(**k): reg.append(k)
# --- Kadri Table 1 rows (bearing-located) ---
for _,r in t1.iterrows():
    L=r.arc_crossing_lat; ti=hms(r.implied_impact_utc); tc=time_cls(ti)
    lm=locm(L); loc='inside prior' if (lm>=1e-3 and in99lat(L)) else ('edge of prior (north of 99.5% latitude 25.0 S)' if lm>=1e-4 else 'outside prior')
    if r.line_to_arc_km>100: loc='bearing line misses the arc by %d km'%r.line_to_arc_km
    lab='Kadri text time' if r.event_id.endswith('text') else ('Kadri caption time / Table 1' if r.time_utc=='00:54:30' else 'Kadri 2024 Table 1')
    add(id='K-'+r.time_utc, group='Published: Kadri 2024 (H01W, Cape Leeuwin)', label=lab, receivers='H01W', times=r.time_utc,
        bearing=f"{r.bearing_deg:.2f} deg", implied_lat=round(L,2), implied_lon=round(r.arc_crossing_lon,2), implied_impact=r.implied_impact_utc,
        time_test=tc, location_test=loc, prior_mass_1deg=round(lm,4), bearing_test=r.bearing_verdict, energy_test='level not measured (module detector did not find it on the digitised trace)' if pd.isna(r.panel_min_p) else 'see module single', known_event='')
R=pd.DataFrame(reg)
# Royer/known flags for Kadri rows
R.loc[R.times=='00:52:03','known_event']='Inside Royer event A pick bar 00:51:56.8-00:52:04.5 (icequake 57.30 S 88.97 E, origin 00:16:29); also Royer event 2 (uncertain, 64.51 S 127.05 E)'
R.loc[R.times=='00:51:50','known_event']='Royer event A / event 2 H01W picks 00:51:38.6-00:51:43.0 (table time; figure marks 14-16 s later)'
R.loc[R.times=='00:54:30','known_event']='Royer appendix arrow 00:54:24.1 = event 5 (uncertain, 49.76 S 133.11 E, origin 00:28:51)'
print(R[['times','implied_lat','implied_lon','implied_impact','time_test','location_test','prior_mass_1deg','bearing_test','energy_test']].to_string())
# energy for text & caption from singles
print(s[s.rx=='H01W'][['time_utc','det','p','eta_needed','eta_min','eta_min_xF35A','implied_source','implied_impact_utc']])