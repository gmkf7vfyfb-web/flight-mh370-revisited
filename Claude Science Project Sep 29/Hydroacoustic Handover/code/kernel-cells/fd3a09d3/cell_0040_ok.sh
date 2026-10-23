cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
grep -rl "T_C2" --include=*.json . | head; python - <<'EOF'
import json
for f in ['stageB/pd_samples_summary.json','stageA/summary_union.json','blackman_noise/blackman_noise_summary.json']:
    try:
        d=json.load(open(f)); s=json.dumps(d); 
        import re
        i=s.find('T_C2'); print(f, len(s), s[max(0,i-200):i+300] if i>=0 else list(d.keys())[:10])
    except Exception as e: print(f, e)
d=json.load(open('stageA/summary_union.json'))['fits']; print([k for k in d if 'T_C2|or|0.05' in k]); print(d['3376|T_C2|or|0.05']); print(d['3274|T_C2|or|0.05'])
b=json.load(open('blackman_noise/blackman_noise_summary.json')); print(json.dumps(b['stations'])[:1500]); print(b['verdict'])
EOF