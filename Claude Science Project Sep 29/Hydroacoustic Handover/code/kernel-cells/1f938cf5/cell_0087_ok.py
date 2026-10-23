
def g(case,cls,fam='all',col='p90'):
    return TAB[(TAB.case==case)&(TAB.cls==cls)&(TAB.family==fam)][col].iloc[0]
def so(oc,cls,col): return SO[(SO.ocean==oc)&(SO.cls==cls)][col].iloc[0]
def f2(x): return f'{x:.2f}'
def e2(x): return f'{x:.2g}'
S=site_df.set_index('site')
rowsD=[]
for cls in CLASSES:
    for case,lab in [('runJ_L','run J rows in L'),('kadri_T','Kadri T, 00:52:03'),('kadri_C','Kadri C, 00:54:30'),('J0011_L','planned descents before 00:11 (J0011) in L')]:
        rowsD.append(f"| {CLS_LABEL[cls]} | {lab} | {f2(g(case,cls,col='p50'))} | {f2(g(case,cls,col='p90'))} | {f2(g(case,cls,col='p99'))} | {g(case,cls,col='descent_min_p50'):.0f} | {g(case,cls,col='floated'):.2f} |")
famrows=[]
for cls in ['recorder-detached','fuselage-section']:
    for fn in ['intact','broken','fragmented']:
        famrows.append(f"| {CLS_LABEL[cls]} | {fn} | {g('runJ_L',cls,fn,'n')} | {f2(g('runJ_L',cls,fn,'p50'))} | {f2(g('runJ_L',cls,fn,'p90'))} | {f2(g('runJ_L',cls,fn,'p99'))} |")
ocrows=[f"| {oc} | " + " | ".join(f2(so(oc,c,'p90'))+' / '+f2(so(oc,c,'p99')) for c in CLASSES)+" |" for oc in order]
segrows=[f"| {r.seg} | {r.cmin:.0f} | {r.cmed:.0f} | {r.cmax:.0f} | {r.smin:.0f}-{r.smax:.0f} | {r.aus:.2f} | {r.tid40:.2f} |" for r in SEG.itertuples()]
siterows=[f"| {s} | {r.lat:.4f} | {r.lon:.4f} | {r.depth_m:.0f} | {r.source} | {'' if r.ausseabed_m is None or pd.isna(r.ausseabed_m) else f'{r.ausseabed_m:.0f}'} | {r.gebco_m:.0f} (TID {r.gebco_tid}) | {r.disc2km_min}-{r.disc2km_max} (median {r.disc2km_p50}); AusSeabed share {r.disc2km_aus_frac:.2f} |" for s,r in S.iterrows()]
invrows=[f"| {CLS_LABEL[r.cls]} | {r.dist_p50:.2f} | {r.dist_p90:.2f} | {r.dist_p99:.2f} | {r.dist_max:.2f} | {r.frac_in_strip_wide:.2f} | {r.frac_in_strip_core:.2f} | {r.frac_beyond_arc_on_bearing:.0f} | {r.min_gap_to_arc_km:.1f} |" for r in INVT.itertuples()]
STL={'run-j/run-j-waypoints':'waypoint routes','run-j/run-j-free':'free flight','run-j/run-j-repro-radar':'radar-reproducing','run-j/run-j-descent-climb':'descent-climb','run-j-joined-v2/J0011':'planned descent before 00:11 (J0011)','run-j-joined-v2/J2241':'planned descent from 22:41 (J2241)'}
massrows=[f"| {STL[st]} | {r['P(impact in L)']:.4f} | {e2(r['P(impact point <=2 km, no settling)'])} | {e2(r['P(recorder detached rests <=2 km)'])} | {e2(r['P(recorder in aft fuselage rests <=2 km)'])} | {r.ratio_rec_to_impact:.2f} | {r.ratio_fus_to_impact:.2f} |" for st,r in mabs.iterrows()]
c0=COND[COND.weighting=='w0'].set_index('stratum'); c2=COND[COND.weighting=='w2'].set_index('stratum')
condrows=[f"| {STL[st]} | {e2(c0.loc[st,'P_rec_given_L'])} | {c0.loc[st,'ESS_rec_rows']:.1f} | {int(c0.loc[st,'distinct_parents_rec'])} | {e2(c2.loc[st,'P_rec_given_L'])} | {c2.loc[st,'ESS_rec_rows']:.1f} |" for st in c0.index]
kfrows=[f"| {r.branch} | {CLS_LABEL[r.cls]} | {r.impact_min_dist_HX_km:.1f} | {r.rest_min_dist_HX_km:.1f} | {r.n_rest_le2km} of {r.n} | {r.rest_depth_p05:.0f} / {r.rest_depth_p50:.0f} / {r.rest_depth_p95:.0f} |" for r in KF.itertuples()]
snrows=[f"| {r.branch} | {CLS_LABEL[r.cls]} | {r.impact_min_dist_km:.2f} | {r.rest_min_dist_km:.2f} | {r.n_rest_le2km} of {r.n} ({r.frac_rest_le2km:.1e}) |" for r in SENS.itertuples()]
ttrows=[f"| {CLS_LABEL[r.cls]} | {r.term_off} | {r.p50:.2f} | {r.p90:.2f} | {r.p99:.2f} |" for r in TT.itertuples()]
open('out/_tables.json','w').write(json.dumps(dict(rowsD=rowsD,famrows=famrows,ocrows=ocrows,segrows=segrows,siterows=siterows,invrows=invrows,massrows=massrows,condrows=condrows,kfrows=kfrows,snrows=snrows,ttrows=ttrows)))
print('\n'.join(siterows)); print('\n'.join(massrows)); print('\n'.join(condrows))
