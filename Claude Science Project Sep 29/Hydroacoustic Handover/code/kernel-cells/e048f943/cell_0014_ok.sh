cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
ls data/imos_background/ data/imos/ | head; python -c "
import json;m=json.load(open('data/imos_background/MANIFEST.json'));print(type(m), list(m.keys())[:10] if isinstance(m,dict) else len(m))
import itertools
if isinstance(m,dict):
    for k,v in list(m.items())[:3]: print(k, str(v)[:400])
"
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ | head; du -sh /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ 2>/dev/null
ls prepare/weak_signal/ results-data | grep -i "weak\|inject\|bg\|background" 
ls results-data/ | tr '\n' ' '