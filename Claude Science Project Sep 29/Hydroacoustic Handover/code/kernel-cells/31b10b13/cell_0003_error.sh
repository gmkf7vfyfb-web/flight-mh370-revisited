export GIT_CONFIG_GLOBAL=/dev/null
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | grep -v ignore; git log --oneline -1; cd ..
du -sh hydro repo
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls "$H/results-data" ; ls "$H/results-data/searches_run_j" "$H/results-data/searches_run_j/panels" "$H/results-data/composition_run_j" "$H/results-data/composition_run_j/v2"
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/*  /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2/ /Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ 2>&1