R="repo/Claude Science Project Sep 29"
grep -n "Refresh v2" "$R/threads/master-prompts/hydroacoustics.md" | head
L=$(grep -n "Refresh v2 — 21 October 2026" "$R/threads/master-prompts/hydroacoustics.md" | head -1 | cut -d: -f1)
sed -n "${L},\$p" "$R/threads/master-prompts/hydroacoustics.md" > /tmp/refresh.md; wc -l /tmp/refresh.md