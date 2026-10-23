export GIT_CONFIG_GLOBAL=/dev/null
ls
cd hydro 2>/dev/null && git branch --show-current && git sparse-checkout list && ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/" | head -30; cd ..
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | grep -v config/git; ls "Claude Science Project Sep 29/"; git log --oneline -1; cd ..
df -k /System/Volumes/Data | tail -1