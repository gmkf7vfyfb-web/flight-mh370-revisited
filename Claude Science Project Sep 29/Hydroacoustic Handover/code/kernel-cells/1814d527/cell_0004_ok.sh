B="repo/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md"
wc -l "$B"
grep -n "^## \|^### \|^# " "$B" | head -80