set +e
export GIT_CONFIG_GLOBAL=/dev/null
cd repo; git fetch -q --depth 1 origin claude-science-sep29 2>/dev/null; git checkout -q FETCH_HEAD -- "Claude Science Project Sep 29/results" 2>/dev/null
cd "Claude Science Project Sep 29/results"
echo "=== hydro charts from tonight (png)"; ls -1 hydroacoustics-*.png 2>/dev/null | grep -E 'weak-signal|run-j|tl-grid|searches|injection|composition|imos-ram|blackman|air9|digitis|kadri' 
ls -d hydroacoustics-*/ 2>/dev/null
cd ../../../hydro; git fetch -q origin hypothesis/hydroacoustics 2>/dev/null; git checkout -q origin/hypothesis/hydroacoustics 2>/dev/null; git sparse-checkout add "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" 2>/dev/null
H="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
echo "=== searches results-data"; ls "$H/searches_run_j" 2>/dev/null
echo "=== composition"; ls "$H/composition_run_j" 2>/dev/null | head -30
echo "=== levels"; ls "$H/levels_run_j" 2>/dev/null | head
echo "=== exchange searches"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/* 2>/dev/null | head -40