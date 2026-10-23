cd repo
R="ISO Sept 28 Status/inputs/recovered-v01/crates/hydroacoustics/src/lib.rs"
sed -n 1,40p "$R"; echo ...; sed -n 260,300p "$R"; echo ...; sed -n 363,426p "$R"; echo ...; sed -n 440,608p "$R"
E="Claude Science Project Sep 29/engine"
echo =====IMPACTVIEW; awk '/pub struct ImpactView/,/^}/' "$E/crates/hypothesis/src/lib.rs"