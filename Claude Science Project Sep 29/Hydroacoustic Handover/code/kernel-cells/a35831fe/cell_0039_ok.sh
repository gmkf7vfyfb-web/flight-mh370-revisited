cd hyd; P='Claude Science Project Sep 29/engine/hypotheses/hydroacoustics'
git sparse-checkout add "/$P/results-data/h08s_template/*" "/$P/data/kadri_fig9_digitised/*" 2>&1 | grep -v config/git
ls -la "$P/results-data/h08s_template" "$P/data/kadri_fig9_digitised"; head -3 "$P/results-data/h08s_template/"*.csv 2>/dev/null | head -30