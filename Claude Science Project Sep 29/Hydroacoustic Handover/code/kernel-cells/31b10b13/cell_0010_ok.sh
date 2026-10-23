cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 155,252p prepare/composition_run_j/reduce.py; grep -n "T_0019\|C_SOFAR\b\|C_SOFAR =\|C_SOFAR_SD\|arc_points\|def " prepare/composition_run_j/prereg.py | head; grep -n "^def " prepare/run_j_windows.py | head -30
head -3 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv