cd "hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python -c "
import json;j=json.load(open('results-data/pair_tests/kadri_trace_pairs.json'));print(json.dumps(j,indent=0)[:2500])"; head -5 results-data/pair_tests/kadri_trace_pairs.csv; wc -l results-data/pair_tests/kadri_trace_pairs.csv; grep -n -i -E '1346|1,346|1710|span' prepare/kadri_trace_pairs.py | head; python - <<'E'
import pandas as pd
d="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces/"
for p in "abcde":
    import glob; f=glob.glob(d+f"*panel-{p}-*")[0]; x=pd.read_csv(f); print(p, list(x.columns)[:6], x.iloc[:,0].min(), x.iloc[:,0].max(), len(x))
E