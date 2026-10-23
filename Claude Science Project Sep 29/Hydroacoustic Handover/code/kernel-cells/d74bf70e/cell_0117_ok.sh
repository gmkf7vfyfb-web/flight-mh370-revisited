set -e
timeout 300 git clone -q --filter=blob:none --no-checkout --single-branch -b claude-science-sep29 "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git" repo 2>&1 | tail -2
cd repo && git config --local core.excludesFile "" && git sparse-checkout init --no-cone
printf '%s\n' '/Claude Science Project Sep 29/coordination/' '/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md' '/Claude Science Project Sep 29/ARCHITECTURE.md' > .git/info/sparse-checkout
git checkout -q claude-science-sep29; git log --oneline -6
F="Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"; grep -n '^## ' "$F"
awk '/^## /{n++} n>=7' "$F"