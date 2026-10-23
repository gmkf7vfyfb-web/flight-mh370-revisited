cd repo
git sparse-checkout add "/Claude Science Project Sep 29/engine/" "/ISO Sept 28 Status/inputs/papers/hydroacoustics/" "/ISO Sept 28 Status/inputs/recovered-v01/crates/hydroacoustics/" "/ISO Sept 28 Status/results/worktree-hydroacoustics/" "/ISO Sept 28 Status/code/branch-diffs/hypothesis__hydroacoustics.patch" "/Claude Science Project Sep 29/results/" 2>&1 | tail -2
git checkout -q -b hypothesis/hydroacoustics
E="Claude Science Project Sep 29/engine"
cat "$E/hypotheses/_template/hypothesis.toml"; echo ====RUN; cat "$E/hypotheses/_template/run.toml"; echo ====LIB; cat "$E/hypotheses/_template/lib.rs"
echo ====SRC; cat "$E/hypotheses/src/lib.rs" | head -60
ls "$E/hypotheses/"; cat "$E/hypotheses/Cargo.toml" 2>/dev/null | head -30