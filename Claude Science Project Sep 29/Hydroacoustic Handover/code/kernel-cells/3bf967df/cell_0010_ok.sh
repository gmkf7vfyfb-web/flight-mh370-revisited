cd repo; export HOME=$PWD/../h XDG_CONFIG_HOME=$PWD/../h/.config
git sparse-checkout add "/Claude Science Project Sep 29/engine/crates/satcom/src/lib.rs" 2>&1|tail -1
E="Claude Science Project Sep 29/engine/data"
head -3 "$E/satellite-ephemeris-inmarsat.csv"; grep -n m0019 "$E/satellite-ephemeris-inmarsat.csv"
grep -n -iE 'm0019|00:19:29' "$E/satcom-observations.csv" | head
grep -n -iE '499|4283|offset|GES|ecef|-2368' "Claude Science Project Sep 29/engine/crates/satcom/src/lib.rs" | head -30