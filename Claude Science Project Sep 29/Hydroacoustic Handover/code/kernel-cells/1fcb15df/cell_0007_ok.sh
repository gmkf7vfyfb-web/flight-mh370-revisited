cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
for f in coincidence/pairs.csv coincidence/coincidence_summary.csv imos/imos_candidates.csv imos/imos_windows.csv panels/panel_candidates.csv panels/panel_windows.csv geometry/lags.csv geometry/arrival_check.csv geometry/bearing_h01w.csv named/royer_arrivals.csv named/royer_verdicts.csv; do echo "== $f $(wc -l <$f)"; head -3 $f | cut -c1-600; done
python -c "
import numpy as np;d=np.load('geometry/sample.npz');print({k:d[k].shape for k in d})
d=np.load('panels/panel_series.npz');print({k:d[k].shape for k in list(d)[:40]})"
cat geometry/energy.json | head -c 1500