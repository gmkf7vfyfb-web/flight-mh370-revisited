export GIT_CONFIG_GLOBAL=/dev/null
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" 2>&1 | grep -v ignore; git log --oneline -1; cd ..
ls "repo/Claude Science Project Sep 29/results" | grep -i -E "hydro|composer|graphics" | head -60
du -sh hydro repo