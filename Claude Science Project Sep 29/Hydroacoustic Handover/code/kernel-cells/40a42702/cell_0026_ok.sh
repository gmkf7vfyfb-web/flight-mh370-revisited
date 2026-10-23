cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat results-data/imos1d/calibration_gain.csv | head; python -c "
import json;d=json.load(open('results-data/imos1d/noise_summary.json'));print(json.dumps(d)[:1800])"; echo
head -3 results-data/imos1d/noise_bands.csv
tr '\n' ' ' < /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt | cut -c1-1500; echo
python -c "
import numpy as np;X=np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/impacts32.npy',mmap_mode='r');print(X.shape)"
grep -n "sens\|SENS\|-197\|gain\|def read_volts" -A3 prepare/imos_noise.py | sed -n 1,40p