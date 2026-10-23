cd repo
git ls-tree -r -l --name-only HEAD | grep -i -E 'blackman|kadri-table1|observed-transient|two-station-correlation|aligned-detection-config|raw-triad|ucrl-tr-207323|duncan|imos|curtin|f-35|brown.*icarus|figure-9|fig9' | grep -v 'v01-share-withdrawn' | head -40
echo ==== withdrawn-only count
git ls-tree -r --name-only HEAD | grep -i -E 'kadri-table1|observed-transient|two-station-correlation' | head
echo ==== template
git ls-tree -r --name-only HEAD "Claude Science Project Sep 29/engine/hypotheses/_template" "Claude Science Project Sep 29/engine/hypotheses/src"
git show HEAD:"Claude Science Project Sep 29/engine/Makefile" | grep -n -A4 -E '^scope|^smoke|^hypothesis'