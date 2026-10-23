cd repo/"Claude Science Project Sep 29"
grep -n "^## \|^### " coordination/HYDROACOUSTICS.md | tail -8
echo ----
tail -n 120 coordination/HYDROACOUSTICS.md
echo ----BRIEF
grep -n "Refresh v2" threads/master-prompts/hydroacoustics.md | head