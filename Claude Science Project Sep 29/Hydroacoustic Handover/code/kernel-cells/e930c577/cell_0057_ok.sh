cd "hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; grep -n -E '^RHO_C|^def band_fraction' -A8 prepare/imos_stageB_map.py | head -30; ls results-data/blackman_noise; python - <<'E'
import pandas as pd, json
u=pd.read_csv('results-data/stageA/pd_vs_snr_union.csv'); print(u.groupby(['logger','template','detector','alpha']).size().head(20)); print(u[(u.logger==3376)].head(3))
k=pd.read_csv('results-data/ram_check/imos_tl_ramcorr.csv',dtype={'quantile':str}); print(k[(k.src_depth_m==10)&(k.fc_hz==20)][['quantile','logger','range_km','tl_db','status']].to_string())
d=pd.read_csv('results-data/near_limits/ims_ram_delta.csv'); print(d.head(3)); print(d.path.unique())
E