X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/step2; cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
python - <<E
import pandas as pd, json
d=pd.read_csv("$X/step2_tl.csv"); print(d.status.value_counts().to_dict())
p=d[d.src_depth_m==10].pivot_table(index='fc_hz',columns='path',values='tl_db').round(1); print(p.to_string())
print(d[(d.src_depth_m==10)&(d.path=='f35a-H11S')][['fc_hz','n_modes_first','n_modes_min']].T.to_string())
o=pd.read_csv("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/f35a_cal/f35a_tl.csv"); print(o[o.src_depth_m==10].pivot_table(index='fc_hz',columns='station',values='tl_db').round(1).T.to_string())
print(json.dumps(json.load(open("$X/step2_tl_meta.json"))['crosscheck_vs_9oct_export']))
E