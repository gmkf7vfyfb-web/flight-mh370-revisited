set -e
export GIT_CONFIG_GLOBAL=/dev/null
if [ ! -d hydro ]; then
git clone -q --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited" hydro 2>&1 | grep -v 'config/git/ignore' || true
cd hydro && git sparse-checkout set "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/engine/config" "Claude Science Project Sep 29/engine/.sources" 2>&1 | grep -v 'config/git/ignore' || true
else cd hydro; fi
git log -1 --format='%h %ad %s' --date=short
H="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
du -sh "$H"; ls "$H"; ls "$H/prepare" | wc -l
echo "=== hypothesis.toml"; grep -n -i -E 'imos|path|env|kraken|status|python' "$H/hypothesis.toml" | head -20
echo "=== imos manifest"; head -c 800 "$H/data/imos_background/MANIFEST.json"; echo
echo "=== recordings"; head -3 "$H/data/imos/recordings.csv"
echo "=== TL engine imports"; grep -l -i -E 'kraken|parabolic|\bram\b' "$H"/prepare/*.py "$H"/prepare/*/*.py 2>/dev/null | head; grep -rn -E '^(import|from) ' "$H/prepare/air9_tl_validation.py" | head -15
grep -rn -E '/Users/pete|mh370-exchange|conda|envs/' "$H/prepare/run_j_driver.py" "$H/prepare/per_impact_lnl.py" "$H/prepare/air9_tl_validation.py" | head -12