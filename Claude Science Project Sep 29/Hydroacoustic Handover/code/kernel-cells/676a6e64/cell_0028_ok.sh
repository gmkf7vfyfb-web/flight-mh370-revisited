set +e
cd repo
echo "=== module hypothesis.toml data paths / env hints"; git show FETCH_HEAD:"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/hypothesis.toml" | grep -n -i -E 'imos|path|env|kraken|ram|python|conda' | head -30
echo "=== imos manifest"; git show FETCH_HEAD:"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/imos_background/MANIFEST.json" | head -30
echo "=== imos recordings csv head"; git show FETCH_HEAD:"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/imos/recordings.csv" | head -3
echo "=== how TL is computed (imports in tl scripts)"; for f in prepare/air9_tl_validation.py prepare/imos_stageB_tl.py prepare/exploratory/run_ims_tl.py prepare/run_j_driver.py prepare/per_impact_lnl.py; do echo "--- $f"; git show FETCH_HEAD:"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/$f" 2>/dev/null | grep -n -E '^(import|from)|kraken|KRAKEN|ram\b|RAM|subprocess|/Users/pete|mh370-exchange|conda|env' | head -25; done