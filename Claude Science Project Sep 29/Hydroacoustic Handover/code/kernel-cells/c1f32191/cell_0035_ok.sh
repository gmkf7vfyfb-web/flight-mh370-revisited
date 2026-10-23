cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("reduce.py").read()
old=s[s.index("                    rows.append(dict(option=key.split(\"/\")[0], p=float(key.split(\"/p\")[1]), alpha=a, receivers=\"IMS proxy + IMOS\" if ims else \"IMOS gated\", lat_lo=lo, lat_hi=hi,\n                                     share=float(W)"):s.index("    return pd.DataFrame(rows)\n\n\ndef evidence_three_ways")]
new='''                    rows.append({"option": key.split("/")[0], "p": float(key.split("/p")[1]), "alpha": a, "receivers": "IMS proxy + IMOS" if ims else "IMOS gated", "lat_lo": lo, "lat_hi": hi,
                                 "share": float(W), "ess": float(W * W / W2) if W2 > 0 else 0.0, "eta95_bayes_logu_1e-6_1e-2": float(eta95),
                                 "eta_excl95_classical": excl, "pnd_at_1e-2": float(P[-1]), "pnd_at_1e-3": float(P[np.argmin(abs(LETA + 3))]),
                                 "pnd_at_anchor": float(np.interp(np.log10(R.ETA_ANCHOR), LETA, P)), "pnd_at_1e-4": float(P[np.argmin(abs(LETA + 4))]),
                                 "L_at_1e-2": float(L[-1]), "L_at_anchor": float(np.interp(np.log10(R.ETA_ANCHOR), LETA, L)), "L_marg": float(L.mean()),
                                 "posterior_median_eta": float(10 ** np.interp(0.5, cdf, LETA))})
'''
s=s.replace(old,new); open("reduce.py","w").write(s); print("patched")
EOF
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -2 $S/_w_run-j-waypoints_1.log; tail -3 $S/driver.log