cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
w=open("worker.py").read()
w=w.replace('''STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: RAM-grid IMOS TL, amplitude variant, statistics only''','''STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: RAM-grid IMOS TL, amplitude variant, statistics only
RAMGRID = STATS_ONLY or os.environ.get("B11_IMOS_RAMGRID") == "1"   # A4: column rewrite with the corrected IMOS table = B11_IMOS_RAMGRID=1 python driver.py''')
w=w.replace('''    M = Machinery(imos_ramgrid=STATS_ONLY); t0 = time.time()
    sd = R.RUN_J''','''    M = Machinery(imos_ramgrid=RAMGRID); t0 = time.time()
    sd = R.RUN_J''')
w=w.replace('''    M = Machinery(imos_ramgrid=STATS_ONLY); t0 = time.time(); z = np.load(R.SUPPLEMENT)''','''    M = Machinery(imos_ramgrid=RAMGRID); t0 = time.time(); z = np.load(R.SUPPLEMENT)''')
w=w.replace('''imos_tl="imos_tl_ram_arc.csv (A4)" if STATS_ONLY else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share))
    summ["imos_tl"] = "imos_tl_ram_arc.csv (A4)" if STATS_ONLY else "imos_tl_ramcorr_arc.csv"''','''imos_tl="imos_tl_ram_arc.csv (A4)" if RAMGRID else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share))
    summ["imos_tl"] = "imos_tl_ram_arc.csv (A4)" if RAMGRID else "imos_tl_ramcorr_arc.csv"''')
open("worker.py","w").write(w); import ast; ast.parse(w); print("ok")
EOF
sed -i '' 's/Rewrite recipe: python driver.py (writes to run-j-gated.staging, ~6.3 GB, needs >= 28 GiB free)./Rewrite recipe: B11_IMOS_RAMGRID=1 python driver.py (writes to run-j-gated.staging, ~6.3 GB, needs >= 28 GiB free)./' /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/README.txt; grep -c "B11_IMOS_RAMGRID" /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/README.txt