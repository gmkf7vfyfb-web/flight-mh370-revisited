cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
python tl_grid_table.py /tmp/tlg_tables_A $OUT/raw/passA 2>&1 | tail -30
python - <<'EOF'
import pandas as pd, numpy as np
d=pd.read_csv('/tmp/tlg_tables_A/tl_grid.csv.gz')
print(d.groupby(['receiver','status']).size().unstack(fill_value=0))
c=pd.read_csv('/tmp/tlg_tables_A/comparison_old_vs_new.csv'); s=c[c.check=='same_point_same_method'].dropna(subset=['delta_db'])
print(s.sort_values('delta_db',key=abs,ascending=False).head(8)[['receiver','point','fc_hz','src_depth_m','tl_old','tl_new','range_old','range_new','delta_db']].to_string())
print(c[c.check=='same_point_same_method'].groupby(['receiver']).apply(lambda g: pd.Series(dict(n=len(g), nan_new=g.tl_new.isna().sum(), nan_old=g.tl_old.isna().sum()))))
EOF