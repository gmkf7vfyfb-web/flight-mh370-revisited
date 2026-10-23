cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; H=origin/hypothesis/hydroacoustics; B=origin/claude-science-sep29
git sparse-checkout add "/$P/results/hydroacoustics-bibliography.csv" "/$P/results/hydroacoustics-literature-review.md" "/$P/results/hydroacoustics-prior-work-critique.md" "/$P/threads/master-prompts/hydroacoustics.md" 2>&1 | grep -v ignore || true
git checkout -q -B fix-hydro $H 2>&1 | grep -v ignore || true
git log -1 --format='%h %s' | cut -c1-90
for x in results/hydroacoustics-bibliography.csv results/hydroacoustics-literature-review.md results/hydroacoustics-prior-work-critique.md; do
  cur=$(git rev-parse HEAD:"$P/$x" | cut -c1-8); echo "$x hydro-blob=$cur"
done
echo "(old sep29 blobs were: bibliography eb7ffd57, literature-review 3685b22f, critique 07effdf7)"