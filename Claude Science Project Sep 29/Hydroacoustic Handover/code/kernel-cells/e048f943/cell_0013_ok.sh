cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
ls results-data/imos1d results-data/imos2b results-data/kadri_fig9_noise results-data/blackman_noise results-data/stageA results-data/stageB
echo ---imos1d
head -3 results-data/imos1d/noise_bands.csv; cut -d, -f1-3 results-data/imos1d/noise_bands.csv | sort -u | head -30
echo ---imos2b
python -c "import json;d=json.load(open('results-data/imos2b/summary.json'));print(list(d.keys()));print(d['background_spl_median'])"
echo ---blackman
python -c "
import json;d=json.load(open('results-data/blackman_noise/blackman_noise_summary.json'));print(list(d.keys()));s=d['stations'];print(list(s.keys()));h=s['H01W'];print(list(h.keys()));print({k:(v if not isinstance(v,dict) else list(v.items())[:2]) for k,v in h.items()})" 2>&1 | head -30
cat results-data/blackman_noise/blackman_noise_offsets.json
echo ---kadri
ls results-data/kadri_fig9_noise; head -c 1500 results-data/kadri_fig9_noise/*.json 2>/dev/null | head -60
echo ---imos_noise doc
sed -n 1,40p prepare/imos_noise.py