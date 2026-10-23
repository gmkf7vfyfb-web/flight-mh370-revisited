cd "audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; grep -rl "noise-vs-impact" . ../../../ 2>/dev/null | head; python3 -c "
import json;d=json.load(open('results-data/blackman_noise/blackman_noise_summary.json'))
print(d['verdict'])
for st,v in d['stations'].items():
  print(st,v['n_unique'],v['n_ok'],{k:round(x['median'],1) for k,x in v['psd_R_band_db'].items()}, {k:(round(x['q10'],1),round(x['q90'],1)) for k,x in v['psd_R_band_db'].items()})
"; cat results-data/blackman_noise/blackman_noise_offsets.json | head -40; python3 -c "
import json;d=json.load(open('results-data/blackman_noise/scenario_markers.json'));print(json.dumps(d)[:3000])"