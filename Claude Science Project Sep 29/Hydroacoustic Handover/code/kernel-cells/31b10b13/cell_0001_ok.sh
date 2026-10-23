export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git clone -q --depth 1 --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse "$URL" hydro
cd hydro && git sparse-checkout set "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" "Claude Science Project Sep 29/coordination" && cd ..
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "$URL" repo
cd repo && git sparse-checkout set "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" && cd ..
du -sh hydro repo
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls "$H"; ls "$H/results-data" ; ls "$H/results-data/searches_run_j" "$H/results-data/searches_run_j/panels" "$H/results-data/composition_run_j" "$H/results-data/composition_run_j/v2" 2>&1 | head -80