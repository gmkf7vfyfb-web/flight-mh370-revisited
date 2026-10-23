set -e
cd ~ 2>/dev/null || true
cd "$OLDPWD" 2>/dev/null || true
W=$PWD; echo $W
rm -rf repo
git clone --filter=blob:none --no-checkout --single-branch -b claude-science-sep29 "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git" repo 2>&1 | tail -2
cd repo
git sparse-checkout init --no-cone
printf '%s\n' '/Claude Science Project Sep 29/ARCHITECTURE.md' '/Claude Science Project Sep 29/threads/' '/Claude Science Project Sep 29/coordination/' '/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/' '/Claude Science Project Sep 29/engine/Makefile' '/ISO Sept 28 Status/threads/master-prompts/common.txt' > .git/info/sparse-checkout
git checkout -q claude-science-sep29
git log --oneline -5
ls "Claude Science Project Sep 29/coordination/"
ls -la "Claude Science Project Sep 29/threads/master-prompts/"
ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/" 2>&1 | head
wc -c "ISO Sept 28 Status/threads/master-prompts/common.txt" "Claude Science Project Sep 29/ARCHITECTURE.md"