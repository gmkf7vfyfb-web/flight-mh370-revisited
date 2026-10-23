cd repo
A="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces"
for p in a b c d e; do f=$(git ls-tree -r FETCH_HEAD --name-only | grep "figure9-panel-$p-"); n=$(git show "FETCH_HEAD:$f" | wc -l); echo "panel $p rows=$n"; done
git show "FETCH_HEAD:$A/kadri-2024-figure9-panel-a-H01W.csv" | head -3
cd "Claude Science Project Sep 29"
echo "=== panel a / 00:27 / weak mentions"; grep -rn -i -E 'panel ?\(?a\)?|00:27|weak signal' results/hydroacoustics-literature-review.md results/hydroacoustics-prior-work-critique.md results/hydroacoustics-kadri-table1-test.md results/hydroacoustics-kadri-northern-run-j.md results/hydroacoustics-pair-tests-oct09.md 2>/dev/null | cut -c1-300 | head -20
echo "=== geometry csv (fits arc?)"; cd ..; git show "FETCH_HEAD:Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/kadri2a/kadri_table1_geometry.csv" | head -3