set -e
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git clone -q --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse "$URL" hydro
cd hydro && git sparse-checkout set "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/threads" && cd ..
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "$URL" repo
cd repo && git sparse-checkout set "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" && cd ..
mkdir -p tools && tar xzf "{{artifact:1bd321c2-571c-42e1-a8f4-b0a2c3eff82e}}" -C tools
ls tools
cd hydro; git log -1 --format='%h %ci %s'; cd ../repo; git log -1 --format='%h %ci %s'
ls "repo/Claude Science Project Sep 29/results" | grep -i hydro | head -50
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/"
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/" | wc -l