cd "repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; ls; ls data scripts 2>/dev/null; head -5 data/air9_residuals.csv 2>/dev/null; wc -l data/air9_residuals.csv 2>/dev/null
cd "../../../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== data/stub, ocean_paths"; ls data/stub | head; ls data/ocean_paths | head -40
echo "=== results-data f35a_cal, nx2d, ram_check, stageB"; ls results-data/f35a_cal results-data/nx2d results-data/ram_check
echo "=== papers?"; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "brown\|\.pdf" | head -20
echo "=== rescore grid header"; head -3 results-data/air9_ew0112/air9_reference_rescore_grid.csv; head -3 results-data/air9_ew0112/air9_posthoc_hflat_plus_array_factor_grid.csv; head -3 results-data/air9_ew0112/air9_farfield_array_factor.csv; cat results-data/air9_ew0112/ewing_20gun_layout_ofr95228.csv