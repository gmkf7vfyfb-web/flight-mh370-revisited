cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"; ls tl_recal_block9 imos_ram_grid | head -30; python - <<'EOF'
import pandas as pd, glob
for f in glob.glob('tl_recal_block9/*ram*.csv')+glob.glob('imos_ram_grid/*.csv')+glob.glob('ram_check/*.csv'):
    try:
        d=pd.read_csv(f)
        if 'wall_s' in d: print(f, d.shape, d[[c for c in d.columns if c in ('fc_hz','wall_s','range_km','tag')]].head(6).to_string())
    except Exception as e: pass
EOF