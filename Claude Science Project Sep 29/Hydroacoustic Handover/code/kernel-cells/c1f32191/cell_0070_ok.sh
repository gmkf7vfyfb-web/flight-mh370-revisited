cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
r=open("reduce.py").read()
r=r.replace('''    json.dump(nd, open(out / "nd_alone_1deg.json", "w"), indent=0)''','''    json.dump(nd, open(out / "nd_alone_1deg.json", "w"), indent=0)
    # non-detection-only combined distribution at 1-degree resolution (removes the amplitude-blind matches, gap G11-1)
    e1 = R.LAT_BAND_EDGES_1DEG; rows_nd = []
    for j, key in enumerate(KEYS):
        for ims in (False, True):
            wP = mx[f"wPnd{'_ims' if ims else ''}_{ALPHA_TAGS[R.ALPHA_PRIMARY]}"][j][1:22, :NG].mean(1); w = mx["sum_w"][j][1:22]
            core = w / w.sum(); comb = wP / wP.sum()
            med = lambda d: float(np.interp(0.5, np.cumsum(d), e1[1:])); n33 = lambda d: float(d[e1[:-1] >= -33].sum())
            with np.errstate(divide="ignore", invalid="ignore"):
                kl = float(np.nansum(np.where(core > 0, core * np.log(core / np.where(comb > 0, comb, np.nan)), 0.0)))
            rows_nd.append(dict(option=key.split("/")[0], p=float(key.split("/p")[1]), receivers="IMS proxy + IMOS" if ims else "IMOS gated", lnZ_nd=float(np.log(wP.sum() / w.sum())),
                                median_lat_core_1deg=med(core), median_lat_combined_nd=med(comb), shift_median_deg=med(comb) - med(core),
                                mass_north_33S_core=n33(core), mass_north_33S_combined_nd=n33(comb), KL_nats=kl))
    pd.DataFrame(rows_nd).to_csv(out / "evidence_nd_only_1deg.csv", index=False)''')
open("reduce.py","w").write(r)
t=open("tables.py").read()
t=t.replace('''    # --- families''','''    nd1 = pd.read_csv(out / "evidence_nd_only_1deg.csv")
    L.append("\\n**Table 4b. The same with the non-detection likelihood only (amplitude-blind time matches removed; 1° resolution).**\\n")
    L.append("| Option | p | receivers | ln Z (ND only) | median lat core | combined | shift (°) | north of 33°S core | combined | KL (nats) |"); L.append("|---|---|---|---|---|---|---|---|---|---|")
    for o in R.OPTIONS:
        for p in R.PS:
            for rx in ("IMOS gated", "IMS proxy + IMOS"):
                z = nd1[(nd1.option == o) & (nd1.p == p) & (nd1.receivers == rx)].iloc[0]
                L.append(f"| {OPT[o]} | {p:g} | {rx} | {z.lnZ_nd:+.4f} | {z.median_lat_core_1deg:.2f} | {z.median_lat_combined_nd:.2f} | {z.shift_median_deg:+.3f} | {z.mass_north_33S_core:.4f} | {z.mass_north_33S_combined_nd:.4f} | {z.KL_nats:.4f} |")
    # --- families''')
open("tables.py","w").write(t); print("ok")
EOF
O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; OMP_NUM_THREADS=1 python reduce.py $O $O/reduce 2>&1 | grep -v Warn | tail -1; python tables.py $O/reduce > $O/reduce/tables.md 2>/dev/null; grep -A 30 "Table 4b" $O/reduce/tables.md | head -30