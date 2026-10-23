cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
python - <<'EOF'
import pandas as pd
a=pd.read_csv('ram_check/imos_tl_ramcorr.csv',dtype={'quantile':str,'logger':str}); a=a[a.src_depth_m==10]
print(a.pivot_table(index=['logger','fc_hz'],columns='quantile',values='tl_db').round(1).to_string())
EOF