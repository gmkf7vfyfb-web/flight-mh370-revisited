X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun-v2; ls -la $X/levels $X/tables $X/repo_copy; ls $X/draws/run-j-waypoints | head -3; python -c "import json;d=json.load(open('$X/run.json'));print({k:(v if len(str(v))<300 else str(v)[:300]) for k,v in d.items()})"; head -3 $X/tables/detectable.csv; grep -n "eta\b\|0.001" $X/tables/detectable.csv | head -0; python - <<'E'
import pandas as pd
X='/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun-v2/tables/'
d=pd.read_csv(X+'detectable.csv'); print(d[d.eta.isin([1e-3,2.1e-4,1e-5])][['key','receiver','eta','frac_matched_filter','frac_baseline','level_q50','snr_q50']].to_string())
o=pd.read_csv('hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/levels_run_j/detectable.csv'); print(o[(o.key=='D0/p0.5')&o.eta.isin([1e-3,2.1e-4,1e-5])][['receiver','eta','frac_matched_filter','frac_baseline','level_q50','snr_q50']].to_string())
E