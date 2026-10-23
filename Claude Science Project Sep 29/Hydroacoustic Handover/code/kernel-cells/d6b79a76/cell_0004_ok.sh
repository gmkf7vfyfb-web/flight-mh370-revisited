export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config; mkdir -p $HOME/.config/git; touch $HOME/.config/git/ignore
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "$URL" repo 2>&1 | tail -2
cd repo && git config --local core.excludesFile "" 
git sparse-checkout set --no-cone "/Claude Science Project Sep 29/coordination/" "/Claude Science Project Sep 29/threads/master-prompts/" "/Claude Science Project Sep 29/ARCHITECTURE.md" "/Claude Science Project Sep 29/results/drift-runj-2026-10-17/" "/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/" "/ISO Sept 28 Status/threads/master-prompts/common.txt" 2>&1|tail -2
git log --oneline -1; ls "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/" "Claude Science Project Sep 29/results/drift-runj-2026-10-17/" "Claude Science Project Sep 29/coordination/" | head -60