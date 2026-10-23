cd repo && git checkout -q claude-science-sep29 && timeout 120 git pull -q --ff-only origin claude-science-sep29; git log --oneline -5
F="Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"; grep -n '^## ' "$F"
awk '/^## /{n++} n>=8' "$F"
echo =====; git show --stat --oneline c2a0931 | head -12