export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git clone -q --depth 1 --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse "$URL" hydro 2>&1 | grep -v keychain
cd hydro && git sparse-checkout set "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" "Claude Science Project Sep 29/coordination" 2>&1|tail -2 && cd ..
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "$URL" repo 2>&1 | grep -v keychain
cd repo && git sparse-checkout set "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" 2>&1|tail -2 && cd ..
du -sh hydro repo; ls "repo/Claude Science Project Sep 29/results" | grep -i -E "run-j|air9|weak-signal|searches|imos-ram|graphics|overnight" | head -80