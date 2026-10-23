
# fix single-5 footnote then re-render it
c10 = cands[-1]
_a,_b,_f1,_f2 = texts_for3(c10, ALLROWS[c10["slug"]])
_f2 = _f2.replace("\n"," ").replace("Level: E nan GJ, tau90 nan s (-); SNR =", "No level computed (no source); SNR definition elsewhere:")
draw_candidate(c10, ALLROWS[c10["slug"]], f"{OUT}/{c10['slug']}", _a, _b, _f1, "\n".join(textwrap.wrap(_f2, 355)))
recs=[]
for c in cands:
    for d in ALLROWS[c["slug"]]:
        k, s = verdict(c, d); rx = d["rx"]
        w = d["w1"]-d["w0"]; p = d.get("p")
        recs.append(dict(candidate=c["name"], candidate_kind=c["kind"], defining_receivers="+".join(c["rx"]), defining_times="+".join(hms(t) for t in c["t_obs"]),
            defining_p="+".join(f"{x:.3g}" for x in c["p_obs"]), source_lat=round(c["lat"],3) if np.isfinite(c["lat"]) else None, source_lon=round(c["lon"],3) if np.isfinite(c["lon"]) else None,
            implied_impact_utc=hms(c["t_imp"]), eta_needed=c.get("eta_need"), eta_basis=c.get("eta_basis"), eta_used_for_levels=c.get("eta_line"),
            receiver=rx, data_source=d["kind"], row_label=ROW_LABEL[(rx,d["kind"])].replace("\n",", "),
            window_start_utc=hms(d["w0"]), window_end_utc=hms(d["w1"]), held=d["held"], held_fraction=round(d["cover_frac"],3),
            max_matched_filter=d.get("stat") if d["kind"]!="royer" else None, max_band_excess_db=d.get("stat") if d["kind"]=="royer" else None,
            t_of_max_utc=hms(d["stat_t"]) if "stat_t" in d else None, p_window=p,
            p_window_trials_corrected=(1-(1-p)**max(1.0, w/55.0)) if p is not None else None,
            expected_snr_db=c.get("snr",{}).get(rx), expected_pd=c.get("pd",{}).get(rx), snr_for_pd50_db=c.get("L50",{}).get(rx),
            expected_snr_at_anchor_db=c.get("snr_anchor",{}).get(rx),
            royer_picks_in_window="; ".join(f"{hms(t)} {st} {l or 'unlabelled'}" for t,st,l,e in d["picks"] if d["w0"]<=t<=d["w1"]),
            royer_figure_marks_in_window="; ".join(f"{hms(t)} {kd} {l}" for t,kd,l,o in d.get("marks",[]) if d["w0"]-10<=t<=d["w1"]+10),
            verdict_class=k, verdict=s, reason_not_held=d.get("reason","") if not d["held"] else ""))
MX = pd.DataFrame(recs); MX.to_csv(f"{OUT}/arrival_window_matrix.csv", index=False)
print(MX.shape, MX.verdict_class.value_counts().to_dict())
print(MX[MX.candidate.str.startswith("Pair 1")][["receiver","data_source","held","max_matched_filter","p_window","expected_snr_db","expected_pd","verdict_class"]].round(3).to_string())
