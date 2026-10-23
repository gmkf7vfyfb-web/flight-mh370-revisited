set -e
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
rm -rf hydro repo
git clone -q --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse "$URL" hydro
cd hydro && git sparse-checkout set "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/threads" && cd ..
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "$URL" repo
cd repo && git sparse-checkout set "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" && cd ..
echo CLONED
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/" 
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/kadri_package/" 2>/dev/null
ls "repo/Claude Science Project Sep 29/results/" | grep -i hydro
ls "repo/Claude Science Project Sep 29/threads/work-orders/" "repo/Claude Science Project Sep 29/threads/master-prompts/" | grep -i hydro