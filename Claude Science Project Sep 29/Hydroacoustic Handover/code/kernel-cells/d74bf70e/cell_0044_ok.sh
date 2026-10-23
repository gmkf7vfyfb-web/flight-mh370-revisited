cd repo
git fetch -q origin; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
git status --porcelain | head
git add "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
git status --porcelain | grep -v 'engine/hypotheses/hydroacoustics/' | head
git commit -q -m "Hydroacoustics: scaffold in predictive mode - FDSN station table, WGS84 geodesic, SOFAR arrival, exposure and mode-cutoff relations, 9 tests" && git push -q -u origin hypothesis/hydroacoustics 2>&1 | tail -2
git log --oneline -1
ls "Claude Science Project Sep 29/results/" | head -60
git ls-tree -r --name-only HEAD | grep -i -E 'arc7|seventh|7th.arc|arc-points|bto.*ring' | head