X=/Users/pete/Downloads/mh370-exchange; P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
grep -n -E "w_D|p=0.5|p_factor|stride|sample.npz" $P/geometry.py | head -20
python - <<E
import pandas as pd, numpy as np
t=pd.read_csv('$X/hydroacoustics/run-j-tl-grid/tables/tl_grid.csv.gz')
print(t.status.value_counts()); print(sorted(t.receiver.unique()))
s=t[(t.offset_nm==0)&(t.fc_hz==t.fc_hz.min())&(t.src_depth_m==10)]
s=s.assign(d=(s.src_lat+33.56).abs()); best=s.src_lat.iloc[(s.src_lat+33.56).abs().argsort().iloc[0]]
print('nearest src lat',best)
print(s[s.src_lat==best][['source_id','src_lon','receiver','range_km','azimuth_deg','back_azimuth_deg','status','land_on_track','km_shallower_1000','min_track_depth_m','tl_db','adiabatic_suspect']].to_string())
i=pd.read_csv('$X/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv',nrows=3); print(list(i.columns)); print(i.head(3).T)
E