cd repo
git ls-tree -r --name-only HEAD | grep -i -E 'hydroacoust|/hypotheses/[^/]+/$' | head -30
echo ====
git ls-tree -d --name-only HEAD "Claude Science Project Sep 29/engine/" "Claude Science Project Sep 29/engine/hypotheses/" 2>/dev/null
echo ==== INBOX
cat "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
echo ==== README
cat "Claude Science Project Sep 29/coordination/README.md"