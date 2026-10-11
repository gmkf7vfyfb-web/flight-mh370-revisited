#!/bin/sh
# On Pléiades run C READY: re-verify the columns the composer read, write the H / Ha row-weight contract, run the aimed seabed step.
WS="$1"; P=/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-c; R="$WS/repo/Claude Science Project Sep 29"
until [ -e "$P/READY" ]; do sleep 60; done
echo "Pléiades READY seen $(date -u +%T)"
( cd "$P" && shasum -a 256 -c SHA256SUMS 2>&1 | grep -v ": OK" ) > "$WS/logs/pleiades-sha-at-ready.txt"; echo "sha mismatches: $(wc -l < $WS/logs/pleiades-sha-at-ready.txt)"
cmp -s "$P/SHA256SUMS" "$WS/logs/pleiades-SHA256SUMS-at-compose" && echo "SHA256SUMS unchanged since compose" || echo "SHA256SUMS CHANGED since compose"
[ -s "$WS/logs/pleiades-sha-at-ready.txt" ] && { echo "STOP: Pléiades files differ"; exit 2; }
cmp -s "$P/SHA256SUMS" "$WS/logs/pleiades-SHA256SUMS-at-compose" || { echo "STOP: SHA256SUMS changed; recompose H needed"; exit 3; }
cd "$WS/work" && OMP_NUM_THREADS=1 python3 "$WS/glue/seabed_c.py" finish "$WS/work" /Users/pete/Downloads/mh370-exchange/composer/next-run-c/row-weights H,Ha
RW=/Users/pete/Downloads/mh370-exchange/composer/next-run-c/row-weights
cd "$WS/work/seabed" && OMP_NUM_THREADS=1 WF_SEEDS=1,2,3,4,5,6,7,8 PYTHONPATH="$R/results/settling-run-c-scripts:$R/engine/hypotheses/end-of-flight/smoke" \
  python3 "$R/results/settling-aimed-resample/wf_aimed.py" prep "$R/engine/hypotheses/end-of-flight/smoke" cp1h 40000 $RW/r600-bto+unpowered-H $RW/r600-bto+unpowered-Ha $RW/heldout+unpowered-H $RW/heldout+unpowered-Ha
sh "$WS/glue/settle_c.sh" "$WS" cp1h 4
echo "H seabed done $(date -u +%T)"
