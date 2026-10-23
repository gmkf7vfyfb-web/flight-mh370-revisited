E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i; ls $E/next-i-free | head; echo ===; ls $E/next-i-free/seed-1 2>/dev/null | head; echo ===; python3 -c "
import json
d=json.load(open('$E/next-i-free/seed-1/terminal.json'))
print('TOP KEYS:', list(d.keys())[:30])
import pprint
for k,v in d.items():
    s=json.dumps(v)
    print(k, type(v).__name__, len(s))
" ; echo "=== run.json impact cols"; python3 -c "
import json
d=json.load(open('$E/next-i-free/seed-1/run.json'))
print([k for k in d.keys()])
print('impact_columns:', d.get('impact_columns'))
"