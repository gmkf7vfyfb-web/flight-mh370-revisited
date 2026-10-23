cd "repo/Claude Science Project Sep 29/results"
grep -n -i "locus\|33.6\|00:31:41\|330\|0.069" hydroacoustics-composition-run-j.md | head -30
H="../../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -rln "locus" "$H/prepare" | head; ls "$H/results-data/composition_run_j" "$H/results-data/composition_run_j/v2" | head -40