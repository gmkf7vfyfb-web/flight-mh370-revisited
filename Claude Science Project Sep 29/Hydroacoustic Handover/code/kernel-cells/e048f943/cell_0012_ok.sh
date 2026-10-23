cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
sed -n 230,330p run_j_windows.py
echo ----TT
grep -n "^def \|^FLAGS\|^class " tl_grid_table.py
echo ----B
grep -n "RHO_C\|^def band_fraction\|^def t_eff\|^LOGGERS" imos_stageB_map.py
sed -n "$(grep -n '^def band_fraction' imos_stageB_map.py | cut -d: -f1),+25p" imos_stageB_map.py