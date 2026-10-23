
nh = int((MX.verdict_class=="not held").sum()); ns = int((MX.verdict_class=="should").sum())
MAT_TITLE = f"Of {len(MX)} candidate-receiver cells, {nh} hold no recording; in {ns} cells a held recording should have shown the candidate and shows nothing"
MAT_SUB = ("Rows: the strongest two-site pair, then the five highest-ranked pairs and five highest-ranked single-site signals (ranking by likelihood ratio). Columns: every receiver. "
           "Cell: data held in the predicted arrival window, the largest matched-filter p (or Royer spectrogram peak) in it, and the expected level (dB above the background median) at the coupling the candidate needs.")
MAT_F1 = MAT_F1.replace("Each row is one candidate sound.", "Each row is one candidate sound; the first row is the strongest pair named in the summary.")
mat_code2 = open("track_matrix.py").read().replace("ax.axhline(5, color", "ax.axhline(1, color='#333333', lw=1.0); ax.axhline(6, color").replace("figsize=(17, 11.2)", "figsize=(17, 12.0)")
open("track_matrix.py","w").write(mat_code2); exec(mat_code2)
summ_rows=[]
for c in cands:
    g = MX[MX.candidate==c["name"]]; vc = g.verdict_class.value_counts()
    should = "; ".join(f"{r.receiver} (exp {r.expected_snr_db:+.0f} dB, P_D {r.expected_pd:.2f}, p {r.p_window:.2g})" for r in g[g.verdict_class=="should"].itertuples())
    pres = "; ".join(f"{r.receiver}" + (f" p {r.p_window:.2g}" if pd.notna(r.p_window) else "") for r in g[g.verdict_class=="present"].itertuples())
    eta = c.get("eta_need")
    src = f"{abs(c['lat']):.1f} S {c['lon']:.1f} E, {hms(c['t_imp'],0)}"
    summ_rows.append(f"| {c['name']} | {src} | {eta:.2g} ({eta/RC.ETA_ANCHOR:.0f}x) | {int(g.held.sum())}/15 | {should or '-'} | {pres or '-'} |")
print("\n".join(summ_rows)); print(MX.verdict_class.value_counts().to_dict())
