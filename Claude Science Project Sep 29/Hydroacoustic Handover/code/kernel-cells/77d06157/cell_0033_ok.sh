D="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"; python -c "
import json;v=json.load(open('$D/route1_verdict.json'));print(json.dumps(v)[:1500])"; python - <<E
import pandas as pd
D="$D"
G=pd.read_csv(D+'/route1_grades.csv'); print(G[G.nominal & (G.SL_B==235)].to_string())
C=pd.read_csv(D+'/route1_common_mode_grades.csv'); print(C.columns.tolist()); print(C[C.nominal].to_string() if 'nominal' in C else C.head())
E
sed -n 29,60p "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9_charts.py" | cut -c1-900