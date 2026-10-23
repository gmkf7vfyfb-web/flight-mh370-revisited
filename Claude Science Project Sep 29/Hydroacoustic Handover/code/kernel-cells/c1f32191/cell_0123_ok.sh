export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; cd repo && git show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid.md" | grep -n -i "addendum" -A 6 | grep -i "5 and 8\|5/8\|marginal\|rewrit\|replace\|table" | cut -c1-240 | head -8; cd ..
cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_build.json
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && export B11_STATS_ONLY=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 && python - <<'EOF'
# point the stats-only run at a fresh directory
p=open("prereg.py").read()
p=p.replace('STATS_DIR_RAMGRID = EXCHANGE_OUT / "stats-ramgrid"','STATS_DIR_RAMGRID = EXCHANGE_OUT / "stats-ramgrid-v2"   # A5: re-run on the stable table (the first stats run straddled a table rewrite)')
open("prereg.py","w").write(p); print("ok")
EOF
mkdir -p /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2 && nohup python driver.py 4 > /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2/driver.out 2>&1 &
sleep 5; date -u +%H:%MZ; tail -1 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2/driver.log
printf 'SUPERSEDED: this statistics run (09:54-11:34Z) straddled a rewrite of imos_tl_ram_arc.csv at 11:29:54Z (RAM-grid addendum: 5/8 Hz on every path); seeds launched before and after used different table versions. Use stats-ramgrid-v2 (stable table) and run-j-gated-v2.\n' >> /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid/DONE