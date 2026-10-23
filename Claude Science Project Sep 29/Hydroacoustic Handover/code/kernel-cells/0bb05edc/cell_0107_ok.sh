cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; B=origin/claude-science-sep29
echo "== master prompts"; git ls-tree --name-only $B "$P/threads/master-prompts/" | sed "s|.*/||" 
echo "== coordination"; git ls-tree --name-only $B "$P/coordination/" | sed "s|.*/||"
echo "== top-level docs"; git ls-tree --name-only $B "$P/" | sed "s|.*/||" | head -20
echo "== engine agent docs"; git ls-tree --name-only $B "$P/engine/" | grep -i -E "md$" | sed "s|.*/||"
echo "== ARCHITECTURE.md headings (first 25)"; git show $B:"$P/ARCHITECTURE.md" | grep -n "^#" | head -25 | cut -c1-120