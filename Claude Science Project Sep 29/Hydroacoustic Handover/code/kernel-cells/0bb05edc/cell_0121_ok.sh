cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; H=origin/hypothesis/hydroacoustics
git ls-tree -r --name-only $H | grep -i -E "(^|/)Makefile$|scope" | head -5
f=$(git ls-tree -r --name-only $H | grep -i -E "(^|/)Makefile$" | head -1); echo "makefile: $f"
git show $H:"$f" | grep -n -i -A14 "^scope" | cut -c1-200 | head -30
echo "--- stale items still on hydro branch (results/threads):"
for x in results/hydroacoustics-bibliography.csv results/hydroacoustics-literature-review.md results/hydroacoustics-prior-work-critique.md threads/master-prompts/hydroacoustics.md; do echo "$x: $(git show $H:"$P/$x" 2>/dev/null | grep -c -i -E 'closed access|,closed,|not obtained|F-35 paper and waveforms')"; done