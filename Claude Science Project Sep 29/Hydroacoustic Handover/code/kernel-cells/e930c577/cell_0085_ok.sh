cd leg; E=~/Downloads/mh370-exchange; S="$PWD/../erepo/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"; cat > run_scan.sh <<EOF
#!/bin/bash
cd "$PWD"
echo "lock acquired \$(date -u +%H:%M:%SZ)"
for st in run-j-free run-j-repro-radar run-j-descent-climb run-j-waypoints; do
  python scan_runj_L.py $E/end-of-flight/run-j $E/core/run-j "$S" scan \$st 2>&1 | grep -v -i -E 'proj|ca_bundle'
done
echo "done \$(date -u +%H:%M:%SZ)"
EOF
chmod +x run_scan.sh; echo "queued $(date -u +%H:%M:%SZ)"; lockf -k /tmp/.mh370-heavy.lock ./run_scan.sh > scan.log 2>&1; tail -3 scan.log