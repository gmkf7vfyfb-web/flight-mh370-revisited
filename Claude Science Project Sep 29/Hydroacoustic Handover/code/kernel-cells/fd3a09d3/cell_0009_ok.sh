cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 1,100p prepare/exploratory/pleiades_test/lhyd.py
echo ==== request.json; python -c "
import json;d=json.load(open('data/ocean_paths/request.json'));print(json.dumps(d)[:1500])"
echo ==== imos_tl_ramcorr; head -5 results-data/ram_check/imos_tl_ramcorr.csv; wc -l results-data/ram_check/imos_tl_ramcorr.csv
echo ==== ims_tl_kraken; head -5 results-data/near_limits/ims_tl_kraken.csv; wc -l results-data/near_limits/ims_tl_kraken.csv
echo ==== ims_ram_delta; cat results-data/near_limits/ims_ram_delta.csv | head
ls data/ocean_paths | head -30