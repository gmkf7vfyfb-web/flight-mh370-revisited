export GIT_CONFIG_GLOBAL=/dev/null
ls; ls repo | head; 
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | tail -2; ls "Claude Science Project Sep 29" ; cd ..
if [ -d repo/tools ]; then mv repo/tools tools; fi
ls tools/Kraken
cd hydro && git log --oneline -3 && cd ../repo && git log --oneline -3; cd ..
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" | grep -i -E "ram|tl_grid|levels|imos_tl" 
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data" | head -30
uptime; ps aux | sort -nrk3 | head -8 | awk '{print $3, $11, $12, $13}'