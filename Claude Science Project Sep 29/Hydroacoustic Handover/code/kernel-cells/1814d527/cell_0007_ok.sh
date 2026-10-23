E=/Users/pete/Downloads/mh370-exchange/hydroacoustics
ls -la $E/run-j-windows/ | head -40
echo ===
cat $E/run-j-tl-grid/README.md | head -80
echo ===
head -3 $E/run-j-tl-grid/tables/ims_tl_kraken_arc.csv; wc -l $E/run-j-tl-grid/tables/*.csv
echo ===
python -c "
import numpy as np
z=np.load('$E/run-j-tl-grid/tables/tl_grid.npz',allow_pickle=True)
for k in z.files: print(k, z[k].shape, z[k].dtype)
"