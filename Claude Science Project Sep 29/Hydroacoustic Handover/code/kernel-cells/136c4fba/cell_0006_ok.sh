cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
echo "=== on claude-science-sep29: threads/ coordination/ ==="
git ls-tree -r --name-only origin/claude-science-sep29 -- "$P/threads" "$P/coordination" | head -60
echo "=== hydro hypothesis tree (branch) ==="
find "$P/engine/hypotheses/hydroacoustics" -maxdepth 2 | head -60