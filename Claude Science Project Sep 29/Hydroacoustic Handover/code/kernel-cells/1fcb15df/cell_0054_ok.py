
cands_fb = cands; ALLROWS_fb = ALLROWS; MX_fb = MX.copy()
cands_r = []
c0 = dict(cands_fb[0]); c0["name"] = "Pair 1 (strongest): Cape Leeuwin 00:52:04 + Diego Garcia South 01:12:49"; c0["rank_note"] = f"ranking track: rank {int(sp.rank_lnLR.min())} by ln LR ({float(sp.lnLR.iloc[0]):.2f})"
cands_r.append(c0)
for k_, r in enumerate(rp.sort_values("rank_lnLR").head(5).itertuples(), 2):
    g = pair_geometry(r.rx_a, hms2u(r.t_a), r.rx_b, hms2u(r.t_b))
    g.update(name=f"Pair {k_} (ranked {r.rank_lnLR}): {names[r.rx_a]} {r.t_a} + {names[r.rx_b]} {r.t_b}", rx=[r.rx_a, r.rx_b], t_obs=[hms2u(r.t_a), hms2u(r.t_b)],
             p_obs=[float(r.p_a), float(r.p_b)], det=[f"{r.det_a} {r.band_a}", f"{r.det_b} {r.band_b}"], lag=float(r.lag_s), max_p=float(r.max_p), p_perm=float(r.p_perm),
             rank_note=f"ranking track: rank {r.rank_lnLR} by ln LR ({float(r.lnLR):.2f}); locus there {float(r.locus_lat):.2f}, {float(r.locus_lon):.2f}, impact {r.implied_impact_utc}")
    levels_for2(g); cands_r.append(g)
for k_, r in enumerate(rs.sort_values("rank_lnLR").head(5).itertuples(), 1):
    try: g = single_geometry(r.rx, hms2u(r.time_utc))
    except ValueError: g = single_arc_uniform(r.rx, hms2u(r.time_utc))
    g.update(name=f"Single {k_} (ranked {r.rank_lnLR}): {names[r.rx]} {r.time_utc}", rx=[r.rx], t_obs=[hms2u(r.time_utc)], p_obs=[float(r.p)], det=[f"{r.det} {r.band}"],
             src=r.source, Etau_src="sample rows conditioned on the observed arrival", rank_note=f"ranking track: rank {r.rank_lnLR} by ln LR ({float(r.lnLR):.2f}); implied source there {r.implied_source}, impact {r.implied_impact_utc}")
    k0 = g["kind"]; g["kind"]="_tmp"; levels_for_orig(g); g["kind"]=k0
    cands_r.append(g)
for c in cands_r:
    print(c["name"], "|", f"{c['lat']:.2f} {c['lon']:.2f} {hms(c['t_imp'],0)}" if np.isfinite(c["lat"]) else "-", "| eta", c.get("eta_need"), "|", c["rank_note"])
