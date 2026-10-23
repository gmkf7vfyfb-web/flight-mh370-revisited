cd "repo/Claude Science Project Sep 29/engine"
sed -n 156,160p hypotheses/hydroacoustics/physics.rs
sed -i '' 's|^mod physics;$|// The exposure and cutoff relations are tested now and used once transmission loss and the\n// seafloor depth arrive; until then they are dead code in a non-test build.\n#[allow(dead_code)]\nmod physics;|' hypotheses/hydroacoustics/lib.rs
export HOME=$PWD/../../../.scratchhome CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH CARGO_TARGET_DIR=$PWD/../../../.target
cargo test --offline --release -p mh370-hypotheses 2>&1 | grep -E "test result|FAILED|never used"
cargo build --offline --release 2>&1 | grep -E "^(warning|error)" | grep -v objcopy | head