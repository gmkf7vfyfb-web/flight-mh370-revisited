
FB = f"{OUT}/fallback-by-p"; os.makedirs(FB, exist_ok=True)
for f in os.listdir(OUT):
    if f.startswith("cand") or f.startswith("arrival_window_matrix"): shutil.move(f"{OUT}/{f}", f"{FB}/{f}")
ALLROWS = {}
for k_, c in enumerate(cands_r, 1):
    nm = c["name"].split(":")[0].lower().replace(" (strongest)", "-strongest").replace(" (ranked ", "-ranked").replace(")", "").replace(" ", "")
    c["slug"] = f"cand{k_:02d}_{nm}"
    rows_ = [row_data(rx, kind, c["win"][rx][0], c["win"][rx][2]) for rx, kind in ROWS]; ALLROWS[c["slug"]] = rows_
    a,b,f1_,f2_ = texts_for3(c, rows_); b = b + "\n" + c["rank_note"] + "."
    draw_candidate(c, rows_, f"{OUT}/{c['slug']}", a, b, f1_, f2_)
recs=[]
cands = cands_r
for c in cands:
    for d in ALLROWS[c["slug"]]:
        k, s = verdict(c, d); rx = d["rx"]; w = d["w1"]-d["w0"]; p = d.get("p")
        recs.append(dict(candidate=c["name"], candidate_kind=c["kind"], ranking_note=c["rank_note"], defining_receivers="+".join(c["rx"]), defining_times="+".join(hms(t) for t in c["t_obs"]),
            defining_detectors="+".join(c["det"]), defining_p="+".join(f"{x:.3g}" for x in c["p_obs"]), source_lat=round(c["lat"],3) if np.isfinite(c["lat"]) else None, source_lon=round(c["lon"],3) if np.isfinite(c["lon"]) else None,
            implied_impact_utc=hms(c["t_imp"]), eta_needed=c.get("eta_need"), eta_basis=c.get("eta_basis"), eta_used_for_levels=c.get("eta_line"),
            receiver=rx, data_source=d["kind"], row_label=ROW_LABEL[(rx,d["kind"])].replace("\n",", "),
            window_start_utc=hms(d["w0"]), window_end_utc=hms(d["w1"]), held=d["held"], held_fraction=round(d["cover_frac"],3),
            max_matched_filter=d.get("stat") if d["kind"]!="royer" else None, max_band_excess_db=d.get("stat") if d["kind"]=="royer" else None,
            t_of_max_utc=hms(d["stat_t"]) if "stat_t" in d else None, p_window=p, p_window_trials_corrected=(1-(1-p)**max(1.0, w/55.0)) if p is not None else None,
            expected_snr_db=c.get("snr",{}).get(rx), expected_pd=c.get("pd",{}).get(rx), snr_for_pd50_db=c.get("L50",{}).get(rx), expected_snr_at_anchor_db=c.get("snr_anchor",{}).get(rx),
            royer_picks_in_window="; ".join(f"{hms(t)} {st} {l or 'unlabelled'}" for t,st,l,e in d["picks"] if d["w0"]<=t<=d["w1"]),
            royer_figure_marks_in_window="; ".join(f"{hms(t)} {kd} {l}" for t,kd,l,o in d.get("marks",[]) if d["w0"]-10<=t<=d["w1"]+10),
            verdict_class=k, verdict=s, reason_not_held=d.get("reason","") if not d["held"] else ""))
MX = pd.DataFrame(recs); MX.to_csv(f"{OUT}/arrival_window_matrix.csv", index=False)
vc_ = MX.verdict_class.value_counts().to_dict(); print(MX.shape, vc_)
for c in cands: print(c["slug"], [verdict(c,d)[0][:5] for d in ALLROWS[c["slug"]]])
