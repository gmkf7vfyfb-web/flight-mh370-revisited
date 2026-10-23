
summ_rows=[]
for c in cands:
    g = MX[MX.candidate==c["name"]]
    vc = g.verdict_class.value_counts()
    should = "; ".join(f"{r.receiver} (exp {r.expected_snr_db:+.0f} dB, P_D {r.expected_pd:.2f}, p {r.p_window:.2g})" if pd.notna(r.p_window) else f"{r.receiver} (exp {r.expected_snr_db:+.0f} dB, P_D {r.expected_pd:.2f}, no sample)" for r in g[g.verdict_class=="should"].itertuples())
    pres = "; ".join(f"{r.receiver}/{r.data_source}" + (f" p {r.p_window:.2g}" if pd.notna(r.p_window) else "") for r in g[g.verdict_class=="present"].itertuples())
    eta = c.get("eta_need")
    summ_rows.append(f"| {c['name']} | {abs(c['lat']):.1f} S {c['lon']:.1f} E, {hms(c['t_imp'],0)} |" if np.isfinite(c["lat"]) else f"| {c['name']} | none (impact before 00:19:29) |")
    summ_rows[-1] += f" {('%.2g' % eta) if np.isfinite(eta) else ('unbounded' if eta==np.inf else 'undefined')} | {int(g.held.sum())}/15 | {vc.get('should',0)} | {should or '-'} | {pres or '-'} |"
print("\n".join(summ_rows))
