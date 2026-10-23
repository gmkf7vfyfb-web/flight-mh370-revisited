cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
for f in coincidence/pairs.csv coincidence/coincidence_summary.csv imos/imos_candidates.csv imos/imos_windows.csv named/*.csv geometry/lags.csv geometry/arrival_check.csv geometry/bearing_h01w.csv panels/*.csv; do echo "== $f $(wc -l <$f)"; head -3 $f | cut -c1-700; done
cat geometry/energy.json | head -c 3000; echo; python -c "import numpy as np; d=np.load('geometry/sample.npz'); [print(k,d[k].shape,d[k].dtype) for k in d]"
cat imos/imos_summary.json | head -c 2500