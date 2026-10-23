cd repo; export GIT_CONFIG_GLOBAL=/dev/null
git fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store\|config/git"
git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" "Claude Science Project Sep 29/coordination/architecture.md" | tail -3
git log --oneline HEAD..origin/claude-science-sep29 | head -10
git diff HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep "^+" | head -40