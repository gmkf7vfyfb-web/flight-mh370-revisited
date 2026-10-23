cd repo
R="ISO Sept 28 Status/inputs/recovered-v01/crates/hydroacoustics/src/lib.rs"
wc -l "$R"
grep -n -E 'fn |#\[test\]|const |struct ' "$R" | head -60
E="Claude Science Project Sep 29/engine"
ls "$E/crates/"; grep -n -E 'pub struct ImpactView|pub [a-z_]+:|fn [a-z_]+\(' "$E/crates/hypothesis/src/lib.rs" | head -80