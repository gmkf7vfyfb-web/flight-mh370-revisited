cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== pd_by_eta.csv ==="; head -5 results-data/stageB/pd_by_eta.csv; wc -l results-data/stageB/pd_by_eta.csv
echo "=== pd_by_latitude.csv ==="; head -4 results-data/stageB/pd_by_latitude.csv
echo "=== imos_tl.csv ==="; head -4 results-data/stageB/imos_tl.csv; wc -l results-data/stageB/imos_tl.csv
echo "=== kadri predictions.csv ==="; head -3 results-data/kadri_package/next-run-b/predictions.csv; wc -l results-data/kadri_package/next-run-b/predictions.csv
echo "=== predictions_meta ==="; python3 -m json.tool results-data/kadri_package/next-run-b/predictions_meta.json | head -40
echo "=== run-i-dive tree ==="; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive | head; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive/* 2>/dev/null | head -20