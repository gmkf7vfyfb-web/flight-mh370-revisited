R="repo/Claude Science Project Sep 29"
grep -n "G-TL1" "$R/results/hydroacoustics-run-j-levels.md" "$R/results/hydroacoustics-tl-grid-run-j.md" | head -12
echo ====; tail -c 3500 "$R/coordination/HYDROACOUSTICS.md"
echo ====; grep -n "^## \|^### " "$R/results/hydroacoustics-run-j-levels.md" | head -30