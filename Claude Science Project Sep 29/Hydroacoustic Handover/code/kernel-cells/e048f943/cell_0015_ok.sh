cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
python -c "
import json;m=json.load(open('data/imos_background/MANIFEST.json'));L=m['loggers']
for k,v in L.items(): print(k, {kk:(vv if not isinstance(vv,list) else (len(vv), vv[:2])) for kk,vv in v.items()})
" | cut -c1-600
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background | head; 
for d in /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/*; do echo "$d $(ls $d | wc -l)"; done 2>/dev/null | head
ls results-data/weak_signal/; 
echo ---weak thresholds
grep -n "7 dB\|13\b.*16\|STA/LTA\|snr50\|P_D *= *0.5\|matched" ../../../results/hydroacoustics-weak-signal-methods.md | head -30