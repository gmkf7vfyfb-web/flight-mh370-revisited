P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
X="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid"
wc -l "$P"/tl_grid_ram_subset.py "$P"/ram_tl_check.py "$P"/tl_grid_table.py "$P"/tl_grid_run_j.py "$P"/run_j_levels.py "$P"/kraken_tl.py
echo ----README; cat "$X/README.md" | head -120
echo ----tables; head -5 "$X/tables/imos_tl_ramcorr_arc.csv"; wc -l "$X/tables/imos_tl_ramcorr_arc.csv"; cat "$X/tables/table_points.json" | head -c 600; echo; ls "$X/ram-subset" | head; ls "$X/raw/passA" | head -5; ls "$X/raw/passA" | wc -l