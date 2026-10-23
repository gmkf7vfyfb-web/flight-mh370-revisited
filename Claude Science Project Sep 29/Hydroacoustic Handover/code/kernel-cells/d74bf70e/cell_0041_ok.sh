cd "repo/Claude Science Project Sep 29/engine"
grep -rn "hypothesis.toml" report/*.py crates/mh370/src/*.rs 2>/dev/null | head -5
export HOME=$PWD/../../../.scratchhome; mkdir -p $HOME; export CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup
export PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH
export CARGO_TARGET_DIR=$PWD/../../../.target
cargo test --offline --release -p mh370-hypotheses hydroacoustics 2>&1 | tail -25