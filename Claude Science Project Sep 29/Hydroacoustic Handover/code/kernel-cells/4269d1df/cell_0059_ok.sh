X=/Users/pete/Downloads/mh370-exchange/end-of-flight; head -5 $X/run-j/summary/table-0019-mixture.txt | cut -c1-300; python3 -c "
import json,collections
d=json.load(open('$X/run-j/summary/table-0019-mixture.json'))
c=d['cells']['D0 total q=0.333 (C2 silent)']; print(c['ln_Z'], c['eff_impacts'], c['latitude_q05_q50_q95'], collections.Counter(x[0] for x in c['seed_ln_Z']))
f=json.load(open('$X/run-j/summary/family-evidence-run-j.json')); print(str(f)[:1500])
"; ls $X/run-j-joined-v2/summary; ls $X/run-j/run-j-waypoints/seed-1; cat $X/run-j/run-j-waypoints/seed-1/COLUMNS.txt 2>/dev/null | head -80 | tr '\n' ' '