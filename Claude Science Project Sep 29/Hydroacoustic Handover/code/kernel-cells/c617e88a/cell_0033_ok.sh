cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics; ls results-data/pair_tests results-data/kadri2a results-data/imos1d results-data/stageB; python - <<'E'
import json,glob
for f in glob.glob("results-data/pair_tests/*.json"):
    d=json.load(open(f)); print(f, json.dumps(d)[:1200]); print()
E
head -12 data/kadri_package/windows.csv; ls data/kadri_package