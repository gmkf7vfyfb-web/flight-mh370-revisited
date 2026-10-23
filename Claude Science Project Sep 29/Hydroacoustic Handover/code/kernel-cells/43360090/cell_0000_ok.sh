cd $TMPDIR 2>/dev/null || cd .; pwd
git clone -q --filter=blob:none --no-checkout --single-branch -b claude-science-sep29 https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo 2>&1 | tail -2
cd repo && git config --local core.excludesFile ""
git sparse-checkout init --no-cone
cat > .git/info/sparse-checkout <<'EOF'
/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md
/Claude Science Project Sep 29/ARCHITECTURE.md
/ISO Sept 28 Status/threads/master-prompts/common.txt
/ISO Sept 28 Status/inputs/papers/hydroacoustics/
/ISO Sept 28 Status/results/worktree-hydroacoustics/
/coordination/HYDROACOUSTICS.md
EOF
git checkout -q claude-science-sep29 2>&1|tail -2
find . -path ./.git -prune -o -type f -print | head -100
git ls-tree -r --name-only HEAD | grep -i "two-station\|twostation\|correlation" | grep -v "\.md$" | head -50