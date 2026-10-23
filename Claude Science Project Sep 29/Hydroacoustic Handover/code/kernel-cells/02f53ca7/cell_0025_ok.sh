cd "repo/Claude Science Project Sep 29/results/hydroacoustics-audit/data"; python -c "
import pandas as pd; r=pd.read_csv('air9_residuals.csv'); m=r[(r.model=='M1')&(r.src_depth_m==10)]
print(m.pivot(index='fc_hz',columns='station',values=['obs_tl_db','model_tl_db']).round(2).to_string())
print(r.model.unique())
"
cd "../../../../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"; head -3 f35a_cal/f35a_tl.csv; python -c "
import pandas as pd; t=pd.read_csv('f35a_cal/f35a_tl.csv'); print(t.columns.tolist()); print(t[t.src_depth_m==10].pivot(index='fc_hz',columns='station',values='tl_db').round(1).to_string())
h=pd.read_csv('ram_check/h11_tl_ramcorr.csv'); print(h.head(12).to_string())
"
grep -n "def band_fraction" -A 25 ../prepare/imos_stageB_map.py | head -40