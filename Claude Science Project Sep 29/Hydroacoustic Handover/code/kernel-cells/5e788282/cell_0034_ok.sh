cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/; python - <<'E'
import json
f=json.load(open('run/fits.json')); s=json.load(open('run/summary.json'))
print(s['taus'], s['bank']['3376'], s['bg_median_level_db'], s['n_null_windows'])
for k,v in f.items():
    if '|0.01|' in k and ('M1b' in k or 'M0a' in k): print(k, v.get('L50_re_noise_db'), round(v.get('slope_db',0),2))
t=json.load(open('run/thresholds.json')); print(t['3376'])
E
cat templates/template_build.json | head -c 1500