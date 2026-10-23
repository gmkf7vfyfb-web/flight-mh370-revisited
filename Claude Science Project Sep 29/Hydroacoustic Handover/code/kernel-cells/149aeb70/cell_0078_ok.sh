cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive && head -12 loud_tail_ess.log; echo ...; python3 -c "
import json
a=json.load(open('loud_tail_ess_dive.json')); b=json.load(open('../run-i/loud_tail_ess.json'))
print('dive thresholds W:', {k:f'{v:.3e}' for k,v in a['thresholds_W'].items()})
print('run-i thresholds W:', {k:f'{v:.3e}' for k,v in b['thresholds_W'].items()})
"