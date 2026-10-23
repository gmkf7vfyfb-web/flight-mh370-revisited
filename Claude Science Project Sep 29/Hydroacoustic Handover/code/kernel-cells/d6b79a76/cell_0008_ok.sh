cd ~/Downloads/mh370-exchange/end-of-flight; head -c 1500 run-j/summary/table-0019-mixture.txt; echo; python3 -c "
import json;d=json.load(open('run-j/summary/table-0019-mixture.json'))
for k,v in d['cells'].items():
  if 'total q=0.333 (C2 silent)' in k: print(k, round(v['ln_Z'],3), round(v['eff_impacts']), {n:round(f['share'],4) for n,f in v['families'].items()}, v['latitude_q05_q50_q95'])
print(d.get('strata'), [k for k in d if k not in ('cells',)])
"; ls run-j-joined-v2; ls run-j-joined-v2/* | head -30; cat run-j-joined-v2/README* 2>/dev/null | head -40; ls ../core/run-j/