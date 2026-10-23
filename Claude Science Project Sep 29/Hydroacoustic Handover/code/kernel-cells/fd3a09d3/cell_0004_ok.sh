cd "repo/Claude Science Project Sep 29"
B=threads/master-prompts/hydroacoustics.md
grep -n "^#" $B | head -60
echo ======
awk '/Refresh v2/{f=1} f' $B | head -200 > /tmp/refresh.txt; wc -l /tmp/refresh.txt
echo ====== INBOX last entries headers
grep -n "^## \|^### " coordination/HYDROACOUSTICS.md | tail -8