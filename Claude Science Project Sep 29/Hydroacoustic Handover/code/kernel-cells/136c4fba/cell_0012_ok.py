import json, pandas as pd, numpy as np
B="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/"
c=pd.read_csv(B+"h08s_shots/h08s_cycles.csv")
print("cycles cols:", list(c.columns))
print("n", len(c), "t_shot %.2f..%.2f"%(c.t_shot.min(), c.t_shot.max()))
print(c.head(3).to_string())
t=json.load(open(B+"h08s_template/h08s_template.json"))
print("\ntemplate keys:", list(t.keys()))
print(json.dumps({k:v for k,v in t.items() if not isinstance(v,(list,dict))}, indent=0)[:1200])
ts=pd.read_csv(B+"h08s_template/h08s_template_shots.csv")
print("\ntemplate_shots cols:", list(ts.columns), len(ts))
print(ts.head(3).to_string())
