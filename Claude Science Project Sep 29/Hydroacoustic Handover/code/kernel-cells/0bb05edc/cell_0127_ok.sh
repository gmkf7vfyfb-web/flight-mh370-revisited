cd fix-metz/"Claude Science Project Sep 29"
grep -n -A3 "Unchanged, because they are facts" coordination/architecture.md | cut -c1-260
echo ---; grep -n -B1 -A6 "## Not labels" results/source-access-ledger-2026-10-22.md | cut -c1-260
echo ---; grep -n "^| DATA NOT HELD\|^| CREDENTIAL\|^| HELD\|^| FETCHED\|^| not retrieved\|^| OPEN\|^| LANDING" results/source-access-ledger-2026-10-22.md