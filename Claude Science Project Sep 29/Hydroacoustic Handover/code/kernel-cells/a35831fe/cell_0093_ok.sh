cd hyd; P='Claude Science Project Sep 29/engine/hypotheses/hydroacoustics'
git sparse-checkout add "/$P/prepare/" "/$P/data/" "/$P/results-data/" "!/$P/results-data/**/*.png" "!/$P/results-data/**/*.pdf" 2>&1 | grep -v config/git | tail -3
du -sh "$P"; ls "$P/data/imos" | head; head -3 "$P/data/imos/recordings.csv"