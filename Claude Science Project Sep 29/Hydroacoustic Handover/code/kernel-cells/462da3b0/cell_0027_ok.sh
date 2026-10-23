WS=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4; E="Claude Science Project Sep 29/engine"
EOFM="$WS/stage/eof-15ba915/$E/hypotheses/end-of-flight/smoke/displacement_hist.py"
cd "$WS/stage/hydro-438c9e9/$E/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 RAYON_NUM_THREADS=1
mkdir -p $WS/out
for s in next-free next-repro-radar next-descent-climb next-routes; do
  echo "== $s $(date -u +%H:%M:%SZ)"
  /usr/bin/time -l env PYTHONPATH=. python search_windows.py --runs /Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/$s --eof-module "$EOFM" --out $WS/out/next-run-b/$s --tag next-run-b-$s 2>&1 | grep -E "seed-|validation|maximum resident|real|Error|error|Traceback|File" | head -20
done; echo "done $(date -u +%H:%M:%SZ)"