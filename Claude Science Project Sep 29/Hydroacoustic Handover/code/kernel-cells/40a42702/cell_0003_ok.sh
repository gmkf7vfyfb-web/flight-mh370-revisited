cd "repo/Claude Science Project Sep 29"
echo ---- BRIEF REFRESH v2
awk '/Refresh v2/{f=1} f' threads/master-prompts/hydroacoustics.md | head -260
echo ---- INBOX last entries
grep -n '^## \|^### ' coordination/HYDROACOUSTICS.md | tail -12