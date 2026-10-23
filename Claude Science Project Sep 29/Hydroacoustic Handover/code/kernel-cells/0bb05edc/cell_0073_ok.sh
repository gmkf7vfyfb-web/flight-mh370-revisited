cd /Users/pete/Downloads/flight-mh370-revisited
H=origin/hypothesis/hydroacoustics; B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
git show $H:"$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/REQUESTS.txt" | sed -n '80,84p'
echo ---; git show $B:"$P/threads/master-prompts/hydroacoustics.md" | sed -n '544,548p'
echo --- hydro-branch master prompt same line; git show $H:"$P/threads/master-prompts/hydroacoustics.md" | grep -n "Kadri 2019\|ask Metz" | cut -c1-200
echo --- work orders mentioning Kadri 2019; git grep -n "Kadri 2017/2019\|Kadri 2019" $B -- "$P/threads" | sed "s|^$B:$P/||" | cut -c1-240