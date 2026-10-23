cd repo/"Claude Science Project Sep 29"; grep -rl "publication coverage" results/*.md results/*/*.md 2>/dev/null | head; grep -rn "publication coverage" results/hydroacoustics-*.md | head -5
ls results | grep -i "coverage\|pubcov\|publication"
cd ../../hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; grep -ln "publication coverage" prepare/*.py prepare/*/*.py 2>/dev/null
echo ==== run-c windows note head
sed -n 1,60p ../../../results/hydroacoustics-run-c-windows.md 2>/dev/null | cut -c1-300 || sed -n 1,60p ../../../../repo/"Claude Science Project Sep 29/results/hydroacoustics-run-c-windows.md" | cut -c1-300