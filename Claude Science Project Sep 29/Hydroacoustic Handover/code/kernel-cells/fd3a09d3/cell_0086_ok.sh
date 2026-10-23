sed -n 499,546p /tmp/tl_recal_block9.py
cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
D="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
git ls-tree --name-only origin/hypothesis/hydroacoustics "$D/" | sed 's#.*/##' | tr '\n' ' '; echo
git show origin/hypothesis/hydroacoustics:"$D/air7_ram.csv" | head -20