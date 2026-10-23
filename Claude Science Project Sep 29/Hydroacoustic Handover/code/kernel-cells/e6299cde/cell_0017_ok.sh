cd /Users/pete/Downloads/mh370-exchange/hydroacoustics
head -3 run-j-tl-grid/raw/passA/tl_grid.csv; wc -l run-j-tl-grid/raw/passA/tl_grid.csv; head -3 run-j-tl-grid/raw/passA/sources.csv; wc -l run-j-tl-grid/raw/passA/sources.csv; cat run-j-tl-grid/raw/passA/wall.json | head -c 600; echo; ls run-j-tl-grid/raw/passB | head -3
python -c "
import numpy as np; z=np.load('run-j-windows/pooled.npz'); k=z['keys']; print(k[:6], k.dtype); print(z['arc'].shape)"
sed -n 138,160p "$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal/preregistration.py"
df -k /System/Volumes/Data | tail -1