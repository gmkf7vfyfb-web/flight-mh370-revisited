cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; B=origin/claude-science-sep29
git log origin/claude-science-sep29 -6 --format='%h %ad %an | %s' --date=format:%H:%M | cut -c1-170
echo "--- master prompt lines ~548-558"; git show $B:"$P/threads/master-prompts/hydroacoustics.md" | sed -n '546,560p' | cut -c1-330
echo "--- digitised-sources 158-166"; git show $B:"$P/results/hydroacoustics-digitised-sources.md" | sed -n '158,166p' | cut -c1-330