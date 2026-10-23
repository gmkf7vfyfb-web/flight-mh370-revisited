cd /Users/pete/Downloads/mh370-exchange/pleiades/run-j; python - <<'E'
import numpy as np, json
d=np.load('maps/map-D0.npz',allow_pickle=True); print({k:(d[k].shape,d[k].dtype, (d[k] if d[k].size<5 else '')) for k in d.files})
E
cat surfaces/joint-surface-rho0.25-gcrel.toml | head -40; cat surfaces/cosmo-surface.toml | head -30