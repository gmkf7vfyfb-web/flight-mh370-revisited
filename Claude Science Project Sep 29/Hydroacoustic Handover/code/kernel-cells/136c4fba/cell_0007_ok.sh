cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
echo "=== kadri/h08s data files on this branch ==="
git ls-tree -r --name-only HEAD | grep -iE "kadri|h08s" | head -80
echo
echo "=== repo-wide (all branches, tracked on sep29) kadri figure extraction ==="
git ls-tree -r --name-only origin/claude-science-sep29 | grep -iE "kadri-figure-extraction|figure9|fig9" | head -40