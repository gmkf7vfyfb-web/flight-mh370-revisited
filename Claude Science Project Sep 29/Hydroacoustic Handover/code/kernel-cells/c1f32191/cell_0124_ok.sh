cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
r=open("reduce.py").read()
r=r.replace('''STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"     # amendment A4: RAM-grid IMOS TL + amplitude-weighted variant present in the accumulators''',
'''STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"     # amendment A4: amplitude-weighted variant present in the accumulators (stats-only run)
RAMGRID = STATS_ONLY or os.environ.get("B11_IMOS_RAMGRID") == "1"   # A4: RAM-grid IMOS TL (stats-only run or the v2 column product)''')
r=r.replace('''    S = concat_sub(sub, supp_sub); M = Machinery(imos_ramgrid=STATS_ONLY)''','''    S = concat_sub(sub, supp_sub); M = Machinery(imos_ramgrid=RAMGRID)''')
r=r.replace('''    summary = dict(prereg="90d7181" + (" + A4 e13a32e (RAM-grid IMOS TL, statistics only)" if STATS_ONLY else ""), imos_tl="imos_tl_ram_arc.csv" if STATS_ONLY else "imos_tl_ramcorr_arc.csv",''',
'''    summary = dict(prereg="90d7181" + (" + A4 e13a32e (RAM-grid IMOS TL)" if RAMGRID else ""), imos_tl="imos_tl_ram_arc.csv" if RAMGRID else "imos_tl_ramcorr_arc.csv", imos_tl_built=json.load(open(R.TL_TABLE_DIR_RAMGRID / "imos_tl_ram_build.json")).get("built") if RAMGRID else None,''')
open("reduce.py","w").write(r); import ast; ast.parse(r)
a=open("addendum_tables.py").read()
a=a.replace('''            a, b = sel(uo, o, p, "IMOS gated"), sel(un, o, p, "IMOS gated"); c = sel(un, o, p, "IMOS gated (amplitude-weighted)")''',
'''            a, b = sel(uo, o, p, "IMOS gated"), sel(un, o, p, "IMOS gated"); c = sel(un, o, p, "IMOS gated (amplitude-weighted)") if (un.receivers == "IMOS gated (amplitude-weighted)").any() else None''')
a=a.replace('''| {e(a.eta95_bayes_full_likelihood)} → {e(b.eta95_bayes_full_likelihood)} | {e(c.eta95_bayes_full_likelihood)} |''','''| {e(a.eta95_bayes_full_likelihood)} → {e(b.eta95_bayes_full_likelihood)} | {e(c.eta95_bayes_full_likelihood) if c is not None else 'n/a'} |''')
a=a.replace('''            c = en[(en.option == o) & (en.p == p) & (en.alpha == 0.05) & (en.receivers == "IMOS gated (amplitude-weighted)")].iloc[0]; d = nn[(nn.option == o) & (nn.p == p) & (nn.receivers == "IMOS gated")].iloc[0]''',
'''            ca = en[(en.option == o) & (en.p == p) & (en.alpha == 0.05) & (en.receivers == "IMOS gated (amplitude-weighted)")]; c = ca.iloc[0] if len(ca) else None; d = nn[(nn.option == o) & (nn.p == p) & (nn.receivers == "IMOS gated")].iloc[0]''')
a=a.replace('''| {c.lnZ_hydro:+.3f} / {c.shift_median_deg:+.2f} / {c.KL_core_vs_combined_nats:.3f} |''','''| {(f"{c.lnZ_hydro:+.3f} / {c.shift_median_deg:+.2f} / {c.KL_core_vs_combined_nats:.3f}") if c is not None else 'n/a'} |''')
a=a.replace('''| {b.lnBF_p1_vs_p0_ampweighted:+.3f} |''','''| {(f"{b.lnBF_p1_vs_p0_ampweighted:+.3f}") if pd.notna(b.get('lnBF_p1_vs_p0_ampweighted', np.nan)) else 'n/a'} |''')
a=a.replace('''| {b['lnBF_imos_amp_a0.05']:+.3f} |''','''| {(f"{b['lnBF_imos_amp_a0.05']:+.3f}") if 'lnBF_imos_amp_a0.05' in b and pd.notna(b['lnBF_imos_amp_a0.05']) else 'n/a'} |''')
open("addendum_tables.py","w").write(a); ast.parse(a); print("ok")
EOF
O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2; mkdir -p $O/reduce && B11_IMOS_RAMGRID=1 OMP_NUM_THREADS=1 python reduce.py $O $O/reduce 2>&1 | grep -v Warn | tail -2; python addendum_tables.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/reduce $O/reduce > $O/reduce/addendum_tables.md 2>&1; head -12 $O/reduce/addendum_tables.md | tail -8; grep -A 4 "Table A3" $O/reduce/addendum_tables.md | tail -2