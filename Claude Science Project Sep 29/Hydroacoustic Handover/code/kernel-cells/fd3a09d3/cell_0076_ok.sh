cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
python tl_grid_table.py /tmp/tlg_tables_AB $OUT/raw/passA $OUT/raw/passB > /dev/null
python tl_grid_evidence.py /tmp/tlg_tables_AB /tmp/tlg_ev_AB > /dev/null
python /tmp/note_numbers.py /tmp/tlg_tables_AB /tmp/tlg_ev_AB 2>&1 | head -150