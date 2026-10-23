cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python build_predictions_v2.py /tmp/kp_smoke --seeds-per-stratum 1 2>&1 | tail -30
python - <<'EOF'
import pandas as pd, numpy as np
d=pd.read_csv('/tmp/kp_smoke/predictions.csv'); print(d.shape); print(d.columns.tolist()[:30])
h=d[(d.receiver=='H01W')&(d.offset_nm==0)]
print(h[['lat','weight_D0_p0.5','impact_q50','ke_q50_j','range_km','back_azimuth_deg','sofar_start_q05','sofar_end_q95','blockage','tl_db_10hz','spl_1s_db_5-40hz_eta0.00021','snr_db_eta2.1e-4','eta_for_snr0']].to_string())
print(d.groupby('receiver').blockage.value_counts().unstack(fill_value=0))
EOF