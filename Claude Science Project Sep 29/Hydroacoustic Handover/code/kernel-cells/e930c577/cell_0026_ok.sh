cd "hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python - <<'E'
import pandas as pd
d=pd.read_csv('results-data/kadri_package/next-run-b/predictions.csv')
s=d[(d.bin_lat.between(-27.5,-23.5))&(d.bin_lon.between(99,104))]
print(s.groupby(['bin_lat','bin_lon','station'])[['range_km','tl_db_10hz','tl_db_20hz','blockage']].first().to_string())
print(d.bin_lat.min(), d.bin_lat.max())
E
sed -n 1,80p prepare/kadri_predictions.py