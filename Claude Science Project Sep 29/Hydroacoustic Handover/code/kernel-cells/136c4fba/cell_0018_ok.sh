cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -rn "\b98\b" results-data/*/*.json 2>/dev/null | head -20
echo "=== n_null columns in csvs ==="
for f in $(ls results-data/*/*.csv | head -40); do h=$(head -1 "$f"); case "$h" in *n_null*|*p_perm*|*n_bg*) echo "$f :: $h";; esac; done
echo "=== kadri2a look_elsewhere_null ==="; python3 -m json.tool results-data/kadri2a/look_elsewhere_null.json 2>/dev/null | head -40
echo "=== pair_tests json ==="; python3 -m json.tool results-data/pair_tests/kadri_trace_pairs.json 2>/dev/null | head -60