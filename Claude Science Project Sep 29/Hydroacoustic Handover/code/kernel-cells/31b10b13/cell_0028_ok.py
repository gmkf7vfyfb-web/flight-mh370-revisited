
mass_cache.clear()
import gc; gc.collect()
OUTX="/Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked"; os.makedirs(OUTX,exist_ok=True)
def wrap(d): return (d+180)%360-180
def cav_single(c):
    cv=["C1","C2"]
    if c["source"].startswith("digitised"): cv.append("digitised plot (Kadri 2024 Fig. 9)")
    if c["rx"]=="H08S" and c["det"] in ("M1b","D1","BE"): cv.append("G-S9 raw H08S panel row, airgun survey; residual detectors do not keep it unless det is Z_res/M1b_res")
    if c["rx"]=="3250": cv.append("blocked path (Scott Reef; no P_D fit): no impact can produce it")
    if c["rx"] in R.RECEIVERS_GATED+["3250"] and c["band"]=="2-5": cv.append("2-5 Hz below the 8 Hz hardware corner")
    if c["rx"] in ("3315","3275"): cv.append("null from the paired logger (stand-in, G-S4)")
    if c["rx"] in R.RECEIVERS_GATED: cv.append("eta_needed_searches used pass-A TL (G-S5); eta_level_ref uses the corrected RAM-grid table")
    if c["rx"] in ("H01W","H08S"): cv.append("P_D from IMOS-proxy noise (+4.8 dB triad gain)")
    return "; ".join(cv)
def bearing_text(rx_list, t_list, baz_pred):
    out=[]
    for rx,tt in zip(rx_list,t_list):
        if rx!="H01W": continue
        m=t1[np.abs(t1.t_unix-tt)<=P.BEARING_WINDOW_S]
        if not len(m): out.append("H01W: no Kadri Table 1 bearing within 30 s"); continue
        if not np.isfinite(baz_pred): out.append("H01W: bearings "+",".join(f"{b:.2f}" for b in m.bearing_deg)+"; no predicted bearing"); continue
        parts=[f"{r.time_utc} {r.bearing_deg:.2f} deg (|d|={abs(wrap(r.bearing_deg-baz_pred)):.1f})" for r in m.itertuples()]
        best=min(abs(wrap(b-baz_pred)) for b in m.bearing_deg)
        out.append(f"H01W predicted {baz_pred:.1f} deg vs Table 1 "+"; ".join(parts)+(" -> CONSISTENT (<=10 deg)" if best<=10 else " -> INCONSISTENT (>10 deg)"))
    return " | ".join(out)
# ---- singles table
s=SG.copy()
s["eta_needed"]=s.eta_level_ref; s["eta_x_F35A"]=s.eta_needed/ANCH
s["rank_lnLR"]=s.lnLR.rank(ascending=False,method="min").astype(int)
s["rank_p"]=s.p.rank(method="min").astype(int)
s["label_searches"]=s.label
s["implied_source"]=[f"{a:.2f}S {b:.2f}E" if np.isfinite(a) else "" for a,b in zip(-s.src_lat.fillna(np.nan)*-1, s.src_lon)]
s["implied_source"]=[f"{-a:.2f}S {b:.2f}E" if np.isfinite(a) else "" for a,b in zip(s.src_lat,s.src_lon)]
s["implied_impact_utc"]=[hms(x) if np.isfinite(x) else "" for x in s.src_t]
s["bearing_consistency"]=[bearing_text([r.rx],[r.t_unix],r.baz_H01W if "baz_H01W" in s and np.isfinite(r.baz_H01W) else np.nan) for r in s.itertuples()]
s["caveats"]=[cav_single(r) for r in s.to_dict("records")]
s["status"]="EXPLORATORY; PREDICTIVE, NOT CALIBRATED"
cols_s=["rank_lnLR","lnLR","rank_p","rx","time_utc","det","band","p","p_B","label_searches","source","kadri_label","in_window",
        "ln_ftime","ln_f_amp_given_time","lnB","lnLR_pB","lnLR_no_bearing","lnLR_D2","lnLR_D3","lnLR_D4",
        "eta_needed","eta_x_F35A","eta_needed_searches","eta_post_med","implied_source","implied_impact_utc","src_E_med","baz_H01W","bearing_consistency","n_rows","caveats","status"]
s=s.sort_values(["lnLR","p"],ascending=[False,True])[cols_s]
s.to_csv(f"{OUTX}/ranked_singles.csv.tmp",index=False); os.replace(f"{OUTX}/ranked_singles.csv.tmp",f"{OUTX}/ranked_singles.csv")
# ---- pairs table
p_=PRS.copy()
p_["eta_x_F35A"]=p_.eta_pd50_all_a005/ANCH
p_["eta_level_x_F35A"]=p_.eta_level_locus/ANCH
p_["rank_lnLR"]=p_.lnLR.rank(ascending=False,method="min").astype(int)
p_["rank_p"]=p_.max_p.rank(method="min").astype(int)
p_["label_searches"]=[label_of(x) for x in p_.max_p]
p_["lag_in_range"]=(p_.lag_s>=p_.lag_lo_s)&(p_.lag_s<=p_.lag_hi_s)
p_["kernel_source"]=[f"{-a:.2f}S {b:.2f}E {hms(c)}" if np.isfinite(a) else "" for a,b,c in zip(p_.src_lat,p_.src_lon,p_.src_t)]
p_["bearing_consistency"]=[bearing_text([r.rx_a,r.rx_b],[CID.loc[r.cid_a,"t_unix"],CID.loc[r.cid_b,"t_unix"]], r.locus_baz_H01W if np.isfinite(getattr(r,"locus_baz_H01W",np.nan)) else np.nan) for r in p_.itertuples()]
p_["caveats"]=[" || ".join(["A: "+cav_single(CID.loc[r.cid_a].to_dict()),"B: "+cav_single(CID.loc[r.cid_b].to_dict())]) for r in p_.itertuples()]
top=(p_.rx_a=="H01W")&(p_.t_a=="00:52:04")&(p_.rx_b=="H08S")&(p_.t_b=="01:12:49")&(p_.det_b=="M1b")
p_.loc[top,"caveats"]+=" || BEARING: locus 33.6S 94.5E is at 268.9 deg from H01W (1,812 km) and 144.8 deg from H08S (3,660 km); Kadri publishes 57 or 306.18 deg for the 00:52 signal (text p. 9 and Table 1 caption disagree), neither within 37 deg; nearest Table 1 bearing to 268.9 is 00:52:50 at 274.84 deg, 46 s later (outside the 30 s rule)"
p_["status"]="EXPLORATORY; PREDICTIVE, NOT CALIBRATED"
cols_p=["rank_lnLR","lnLR","rank_p","rx_a","t_a","det_a","band_a","p_a","pB_a","rx_b","t_b","det_b","band_b","p_b","pB_b","max_p","label_searches","family",
        "lag_s","lag_lo_s","lag_hi_s","lag_in_range","n_pairs_obs","p_perm","ln_ftime","ln_f_amp_given_time","lnB","lnLR_pB","lnLR_no_bearing","lnLR_D2","lnLR_D3","lnLR_D4",
        "locus_lat","locus_lon","implied_impact_utc","implied_vs_0019","locus_D0_mass_within_1deg","n_arc_loci","other_loci","locus_baz_H01W","kernel_source",
        "eta_pd50_all_a005","eta_x_F35A","eta_level_locus","eta_level_x_F35A","eta_level_ref_a","eta_level_ref_b","eta_post_med","bearing_consistency","src_a","src_b","kadri_a","kadri_b","n_rows","caveats","status"]
p_=p_.sort_values(["lnLR","max_p"],ascending=[False,True])[cols_p]
p_.to_csv(f"{OUTX}/ranked_pairs.csv.tmp",index=False); os.replace(f"{OUTX}/ranked_pairs.csv.tmp",f"{OUTX}/ranked_pairs.csv")
print(len(s),len(p_)); print(p_.head(5)[["rank_lnLR","lnLR","rx_a","t_a","rx_b","t_b","max_p","locus_lat","eta_pd50_all_a005","eta_x_F35A"]].to_string())
print(p_.loc[top[p_.index]] [["rank_lnLR","lnLR","lnLR_no_bearing","rank_p","locus_lat","locus_lon","implied_impact_utc","eta_pd50_all_a005","eta_x_F35A","locus_baz_H01W","bearing_consistency"]].to_string())
