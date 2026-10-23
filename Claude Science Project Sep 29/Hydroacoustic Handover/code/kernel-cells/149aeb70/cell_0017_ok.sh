R=/Users/pete/Downloads/mh370-exchange/core/run-i; python3 -c "
import json
d=json.load(open('$R/next-i-free/run.json'))
print('IMPACT_COLUMNS:'); print(d['impact_columns'])
print(); print('TERMINAL:'); print(json.dumps(d['terminal'],indent=1)[:3000])
print(); print('HYPOTHESES:'); print(json.dumps(d['hypotheses'],indent=1)[:1200])
print(); print('replicates',d['replicates'],'runtime_s',d['runtime_s'])
"