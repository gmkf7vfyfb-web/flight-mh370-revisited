A="audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; M="audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; OMP_NUM_THREADS=1 python "$A/scripts/markers.py" "$M" "$A/data/air9_residuals.csv" /Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-r600-bto-only.npz "$A/data/markers_audit.json" 2>&1 | tail -12; python3 - <<'EOF'
import json
a=json.load(open("audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/blackman_noise/scenario_markers.json"))
b=json.load(open("audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/data/markers_audit.json"))
for st in ['H01W','H08S']:
  for ka,kb in [("a: F-35A-type entry, 777 mass","a"),("b: ditching, total KE","b_total"),("b: ditching, vertical KE only","b_vertical")]:
    d=[round(b['stations'][st]['scen'][kb][i]['q50']-a['stations'][st][ka][i][1],2) for i in range(10)]
    print(st,kb,'q50 diff vs module',max(map(abs,d)))
EOF