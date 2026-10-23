cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
git log -3 --format='%h %ad | %an | %s' --date=short $B -- "$P/results/restricted-sources-ledger.md" | cut -c1-200
echo ----; git show $B:"$P/results/restricted-sources-ledger.md" | cut -c1-600