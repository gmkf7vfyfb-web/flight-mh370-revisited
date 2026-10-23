export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; mkdir -p $HOME
git clone --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo 2>&1 | tail -2
cd repo && git sparse-checkout set --no-cone "/Claude Science Project Sep 29/coordination/" "/Claude Science Project Sep 29/results/evidence-sweep-2026-10-17/" "/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/" "/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md" 2>&1|tail -2
ls "Claude Science Project Sep 29/results/evidence-sweep-2026-10-17/" "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/" 2>&1
git log --oneline -3