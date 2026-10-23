export GIT_CONFIG_GLOBAL=/dev/null
cd hydro && git sparse-checkout list; git log --oneline -1; ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/" 2>&1 | head; cd ..
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | tail -2; git log --oneline -1; ls "Claude Science Project Sep 29/results" | grep -i hydro; cd ..
du -sh hydro repo