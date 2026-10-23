cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; W=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/0f0b1c26-b241-4b3b-9f87-53c4386c8175; python calibration_events_stage1b.py score $W/stage1b "$W/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/gaspin-shuler" 2>&1 | python -c "
import sys,json; t=sys.stdin.read(); 
try:
  d=json.loads(t)
except Exception: print(t[-3000:]); sys.exit()
for k,v in d['charge'].items():
  if isinstance(v,dict) and 'stats' in v: print(k, {a:round(b,2) for a,b in v['stats'].items()}, v['verdict'], v['grades'])
  else: print(k,v)
for k,v in d['af447'].items(): print(k,v)
print(d['timing'])"