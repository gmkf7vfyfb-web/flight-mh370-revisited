export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config; mkdir -p $HOME
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo 2>&1 | tail -2
cd repo
git sparse-checkout set "Claude Science Project Sep 29/threads/master-prompts" "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/ARCHITECTURE.md" "Claude Science Project Sep 29/results/drift-runj-2026-10-17" "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18" "ISO Sept 28 Status/threads/master-prompts/common.txt" "Claude Science Project Sep 29/engine/hypotheses/debris-drift" 2>&1|tail -2
git log --oneline -3
cd "Claude Science Project Sep 29"; ls; ls coordination | head -50; ls results/drift-runj-2026-10-17 results/kadri-haixun-conditional-2026-10-18 2>&1; ls engine/hypotheses/debris-drift 2>&1 | head