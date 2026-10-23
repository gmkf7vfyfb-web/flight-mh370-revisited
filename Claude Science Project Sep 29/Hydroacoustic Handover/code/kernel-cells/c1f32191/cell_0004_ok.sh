R="repo/Claude Science Project Sep 29"
echo ===== INBOX last entries
grep -n "^## \|^### " "$R/coordination/HYDROACOUSTICS.md" | tail -8
tail -n 220 "$R/coordination/HYDROACOUSTICS.md"