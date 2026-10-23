export GIT_CONFIG_GLOBAL=/dev/null
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | grep -v ignore | tail -3; ls "Claude Science Project Sep 29"; cd ..
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls "$H"; ls "$H/results-data"; ls "$H/results-data/searches_run_j" "$H/results-data/digitised" 2>&1 | head -40; ls "$H/prepare" | tr '\n' ' '