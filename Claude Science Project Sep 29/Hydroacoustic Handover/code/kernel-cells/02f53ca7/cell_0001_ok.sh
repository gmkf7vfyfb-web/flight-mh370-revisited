export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
ls
cd hydro 2>/dev/null && { git log -1 --format='%h %ci %s'; ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/" ; ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" | wc -l; cd ..; }
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>&1 | grep -v 'failed to store\|config/git'; git log -1 --format='%h %ci %s'; ls "Claude Science Project Sep 29/"; ls "Claude Science Project Sep 29/results" | grep -i hydro