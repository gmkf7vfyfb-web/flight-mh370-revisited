cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; E="$P/engine/hypotheses/hydroacoustics"
git sparse-checkout set \
 "/$E/prepare/digitise_brown_2026.py" "/$E/prepare/tl_recal_block9.py" "/$E/prepare/kadri_package/v2-2026-10-22/REQUESTS.txt" "/$E/prepare/kadri_package/v2-2026-10-22/MANIFEST.txt" \
 "/$E/data/blackman/extraction_method.txt" "/$E/data/blackman/receiver_observations_diff_vs_drive.csv" "/$E/results-data/digitised/brown-2026/METHOD.json" \
 "/$P/results/hydroacoustics-bibliography.csv" "/$P/results/hydroacoustics-literature-review.md" "/$P/results/hydroacoustics-prior-work-critique.md" "/$P/threads/master-prompts/hydroacoustics.md" 2>&1 | grep -v ignore || true
git checkout -q -B fix-hydro origin/hypothesis/hydroacoustics 2>&1 | grep -v ignore || true
git log -1 --format='%h %s' | cut -c1-100
for f in results/hydroacoustics-bibliography.csv results/hydroacoustics-literature-review.md results/hydroacoustics-prior-work-critique.md; do echo "$f $(git rev-parse HEAD:"$P/$f" | cut -c1-8)"; done
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/ | grep -i kadri; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2 | head -20