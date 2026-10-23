P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls -la "$P/prepare/kadri_package" "$P/results-data/kadri_package" "$P/data/kadri_package"
find "$P/results-data/kadri_package" -type f | head -50
echo ---WO---
grep -n -i "block 12\|^## \|^### " "repo/Claude Science Project Sep 29/threads/work-orders/hydroacoustics-order-2026-10-21.md" | head -60