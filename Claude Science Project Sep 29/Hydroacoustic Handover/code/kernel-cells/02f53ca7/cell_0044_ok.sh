cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
python -c "
import json,pandas as pd; v=json.load(open('route1_verdict.json')); print(v['verdict']); print(json.dumps(v['nominal'],indent=0))
g=pd.read_csv('route1_grades.csv'); b=g[(g.weights=='V^(1/3)')&(g.sign==1)&(g.ball=='both')&(g.xh==30)&(g.zh==15)]
print(b[['station','zs','SL_B','level','slope','slope_se','shape','g_level','g_slope','g_shape']].round(2).to_string(index=False))
r=pd.read_csv('route1_residuals.csv'); n=r[r.nominal]; print(n[['station','fc_hz','rl_obs_db','rl_pred_db','r_db','S0_db','af_db','dref_db']].round(2).to_string(index=False))
# sensitivities at nominal geometry z10
s=g[(g.zs==10)&(g.xh==30)&(g.zh==15)&(g.SL_B==235)]; print(s[['station','weights','sign','ball','level','slope','shape','g_slope','g_shape']].round(2).to_string(index=False))
"