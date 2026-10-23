P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '235,300p' "$P/tl_grid_table.py"
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/near_limits/" | head; head -3 "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/near_limits/ims_ram_delta.csv"
grep -n "RHO_C\|def band_fraction" "$P/imos_stageB_map.py" | head -5
grep -n "ram_delta\|RAM" "$P/per_impact_lnl.py" | head -20