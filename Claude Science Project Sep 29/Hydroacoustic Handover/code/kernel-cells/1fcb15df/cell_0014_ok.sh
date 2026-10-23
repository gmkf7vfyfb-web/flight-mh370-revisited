D="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/digitised/royer-2016"
ls "$D/spectrograms" | grep npz; head -3 "$D/spectrograms/appendix_h01w2_h01w2_0030-0100_band.csv"
python -c "
import numpy as np;d=np.load('$D/spectrograms/appendix_h01w2_h01w2_0030-0100.npz');print({k:(d[k].shape,d[k].dtype) for k in d}); print(d['t_s'][:3] if 't_s' in d else '')"
cat "$D/royer_stations.csv"; head -5 "$D/royer_arrivals.csv"; head -3 "$D/royer_events.csv"; cat "$D/METHOD.json" | head -c 1500