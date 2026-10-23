cd repo
git config --local core.excludesFile ""
git config --local user.name >/dev/null || git config --local user.name "hydroacoustics module"
git config --local user.email >/dev/null || git config --local user.email "noreply@users.noreply.github.com"
git fetch -q origin claude-science-sep29
echo "remote head: $(git rev-parse --short origin/claude-science-sep29)  local: $(git rev-parse --short HEAD)"
git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" "Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md"
git log --oneline HEAD..origin/claude-science-sep29
git add "Claude Science Project Sep 29/coordination/architecture.md"
git commit -q -m "Coordination: hydroacoustics first entry - plan check, data inventory, positions on brief s14, five questions"
git pull -q --rebase origin claude-science-sep29
git push -q origin HEAD:claude-science-sep29 2>&1 | grep -v '^$' | tail -3
git log --oneline -3