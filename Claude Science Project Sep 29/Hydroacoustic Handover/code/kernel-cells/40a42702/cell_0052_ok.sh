cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
python - <<'EOF'
import json; d=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.json'))
print('rows',d['n_rows'],'seeds',d['n_seeds']); print('tau',{k:[round(x,2) for x in v] for k,v in d['tau'].items() if k.endswith('p0.5')})
print('E_j D0/p0.5 (GJ)',[round(x/1e9,2) for x in d['E_j']['D0/p0.5']]); print('ess',{k:round(v) for k,v in d['ess'].items()})
print({r:[round(x) for x in v] for r,v in d['range_km']['D0/p0.5'].items()})
EOF
uptime
WS=$(pwd | sed 's#/hydro/.*##')
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python templates.py $OUT/inputs/inputs.json $OUT/templates $WS/tools 4 > $OUT/templates.log 2>&1; tail -3 $OUT/templates.log