cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 100,135p prepare/exploratory/pleiades_test/lhyd.py
echo ==== B; grep -n "^RHO_C\|^def band_fraction\|^def t_eff\|^LOGGERS\|^def " prepare/imos_stageB_map.py | head -20
echo ==== imos_noise outputs; sed -n 1,30p prepare/imos_noise.py | head -40; ls results-data/imos1d results-data/imos2b
echo ==== blackman; ls results-data/blackman_noise; cat results-data/blackman_noise/blackman_noise_offsets.json | head -c 1500; echo
python -c "
import json; d=json.load(open('results-data/imos2b/summary.json')); print({k:(v if not isinstance(v,(list,dict)) or len(str(v))<300 else str(v)[:300]) for k,v in d.items()})"