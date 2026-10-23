cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
mkdir -p ../../../../../../charts_out
time python run_j_levels_charts.py $OUT ../../../../../../charts_out 2>&1 | grep -v "^$" | tail -20; ls ../../../../../../charts_out | head -30