export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config
cd repo; P='Claude Science Project Sep 29'
git sparse-checkout set --no-cone "/$P/engine/hypotheses/seabed-search/" "/$P/results/evidence-sweep-2026-10-17/" "/$P/coordination/SEARCHED_AREAS.md" "/$P/threads/master-prompts/searched-areas.md" "/$P/results/seabed-search-references.md" "/$P/results/kadri-haixun-conditional-2026-10-18/" "/$P/results/composer-views-run-j*" "/$P/engine/crates/ocean/prepare/ausseabed_to_grid.py" 2>&1|tail -2
ls "$P/results/evidence-sweep-2026-10-17/" "$P/engine/hypotheses/seabed-search/coverage"; wc -c "$P/results/evidence-sweep-2026-10-17/"*.md "$P/engine/hypotheses/seabed-search/coverage/"*
git ls-tree -r --name-only HEAD -- "$P/results" | grep -iE 'surface-search|seabed-search-' | head -40