cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
git diff --stat fc825c0 4392091~1 -- "$P/per_impact_lnl.py" "$P/tl_grid_run_j.py" "$P/kraken_tl.py" "$P/air9_tl_validation.py" "$P/ram_tl_check.py" "$P/imos_stageB_map.py"; echo "(empty = no concurrent edits to the files I touched or depend on)"