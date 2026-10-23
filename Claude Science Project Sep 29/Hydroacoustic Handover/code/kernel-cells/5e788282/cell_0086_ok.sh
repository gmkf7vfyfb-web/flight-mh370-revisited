cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/metz_f35a"
python - <<'E'
import json
s=json.load(open('step2_summary.json'))
for k in ['tau_used_s','tau_grid_point_s','anchor_eta','eta_at_fallback_tau_3p30','routeB_eta_4_64','routeB_eta_4_64_geomean','U2','old']: print(k, s[k])
sp=s['spread']
for k,v in sp.items(): print(k, v if not isinstance(v,dict) else {a:'%.3g'%b for a,b in v.items()})
r=json.load(open('step4_route2.json'))
for k,v in r.items(): print(k, v.get('n'), round(v.get('slope_db_per_oct',float('nan')),2), round(v.get('slope_se',float('nan')),2), [round(x,2) for x in v.get('envelope',[])], v['verdict'], v.get('bands'))
E