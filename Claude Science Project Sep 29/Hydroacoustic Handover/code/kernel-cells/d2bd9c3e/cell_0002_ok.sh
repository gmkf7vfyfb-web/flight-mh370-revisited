export GIT_CONFIG_GLOBAL=/dev/null
cd hydro && git sparse-checkout reapply 2>&1 | tail -2; ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/" ; cd ..
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | grep -v "failed to store\|config/git" ; ls "Claude Science Project Sep 29"; cd ..
ls hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" | wc -l
ls repo/"Claude Science Project Sep 29/results" | grep -i hydro
ls repo/"Claude Science Project Sep 29/threads/work-orders/"