cd repo/"Claude Science Project Sep 29"
wc -l threads/master-prompts/hydroacoustics.md threads/work-orders/hydroacoustics-order-2026-10-21.md coordination/HYDROACOUSTICS.md coordination/architecture.md results/hydroacoustics-tl-grid-run-j.md results/hydroacoustics-run-j-windows.md results/hydroacoustics-weak-signal-methods.md
grep -n "^## \|^# " threads/master-prompts/hydroacoustics.md | tail -40
echo ---
grep -n "^## \|^### " coordination/HYDROACOUSTICS.md | tail -12