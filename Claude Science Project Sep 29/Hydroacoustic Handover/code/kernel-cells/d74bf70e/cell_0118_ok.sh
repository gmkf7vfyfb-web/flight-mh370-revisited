cd repo
timeout 120 git fetch -q origin hypothesis/hydroacoustics:hypothesis/hydroacoustics && git log --oneline -1 hypothesis/hydroacoustics
B="Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md"; wc -c "$B"; grep -n -i -E '^#+ .*amend' "$B"; awk '/^#+ .*[Aa]mend/{f=1} f' "$B" | head -60
df -g . | tail -1