W=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a; D="$W/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/search_windows"; ls -la "$D" "$D"/*; python3 -c "
import json,sys
s=json.load(open(sys.argv[1]+'/reference-289/summary.json'))
p=s['provenance']; print(json.dumps({k:v for k,v in p.items() if k!='run_json'},indent=0)[:3000]); 
for k,v in list(p['run_json'].items())[:2]: print(k, json.dumps(v)[:1500])
print(len(s['arms'])); print(list(s['arms'])[:80])
" "$D"; ls $W/.tmp; ls $W/.tmp/* | head