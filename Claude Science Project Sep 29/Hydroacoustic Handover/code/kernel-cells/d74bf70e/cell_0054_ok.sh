cd repo
git stash list | head -2; git status --porcelain | head
git fetch -q origin
git checkout -q claude-science-sep29 && git merge -q --ff-only origin/claude-science-sep29
git log --oneline -8
F="Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
grep -n '^## ' "$F"
awk '/^## /{n++} n>=4' "$F"