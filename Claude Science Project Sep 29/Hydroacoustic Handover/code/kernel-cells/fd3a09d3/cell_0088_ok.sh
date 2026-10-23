cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
python tl_grid_table.py /tmp/tlg_tables_AB $OUT/raw/passA $OUT/raw/passB > /dev/null
python - <<'EOF'
import pandas as pd
g=pd.read_csv('/tmp/tlg_tables_AB/tl_grid.csv.gz', dtype={'receiver':str}); p=g.drop_duplicates(['source_id','receiver'])
print(p.groupby('receiver').agg(n=('source_id','size'), suspect=('adiabatic_suspect','mean'), suspect_excl_rx=('adiabatic_suspect_excl_rx','mean'), axis_med=('axis_depth_m','median'), axis_min=('axis_depth_m','min'), axis_max=('axis_depth_m','max')).round(2))
q=p[(p.offset_nm==0)&(p.status!='land')]
for rec,h in q.groupby('receiver'):
    hh=h[h.adiabatic_suspect_excl_rx==1]; print(rec, 'suspect_excl_rx lats:', sorted(hh.src_lat.unique())[:6], '...', len(hh), 'min corridor', hh.min_corridor_depth_m.min() if len(hh) else None)
EOF