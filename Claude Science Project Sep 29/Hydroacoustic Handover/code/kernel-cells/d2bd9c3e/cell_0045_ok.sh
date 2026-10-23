cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export PYTHONPATH=. MPLBACKEND=Agg
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
mkdir -p ../../../../../charts_out
python run_j_windows_charts.py $OUT ../../../../../charts_out --prereg bc99b07 --repo-results "$PWD/../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -5
ls -la ../../../../../charts_out