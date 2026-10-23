rows=[]
for k,cd in CANDS.items():
    lv=lev[k]; q=lambda r: np.median(lv['base'][r])+10*np.log10(2.26e-3)
    cv=cov_at(cd['lat'],cd['lon']); pp=plei_post_at(cd['lat'],cd['lon'])
    rows.append(dict(cand=k,lat=round(cd['lat'],2),lon=round(cd['lon'],2),impact=fmt(cd['t0'])[:8],fit_resid_s=' / '.join(f'{x:+.0f}' for x in cd['resid']),
        routes_within_120km=f"{len(sel[k])} ({100*len(sel[k])/len(RT):.1f}%)", searched=('ATSB Phase 2' if cv[0]>0.5 else ('OI 2018' if cv[1]>0.5 else ('OI 2025-26' if cv[2]>0.5 else 'no'))),
        pleiades_cond_mass_1deg=round(pp[0],3), E_median_GJ=round(lv['Eq'][1]/1e9,2),
        **{f'SNR_F35A_{r}':round(q(r),1) for r in RX4}))
SUM=pd.DataFrame(rows); print(SUM.to_string()); SUM.to_csv('cand/candidates-A-F-summary.csv',index=False)