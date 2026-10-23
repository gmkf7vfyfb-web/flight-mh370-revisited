cd "repo/Claude Science Project Sep 29/engine"
python3 -c "import math;print(1025*1500/(2*math.pi), 1025*1500/(2*math.pi)*1e-10)"
f=hypotheses/hydroacoustics/physics.rs
sed -i '' 's|/// Hand computation: rho c / 2 pi = 1025 \* 1500 / 6.283185 = 244,705.0 Pa^2 s per joule at|/// Hand computation: rho c / 2 pi = 1,537,500 / 6.2831853 = 244,700.7 Pa^2 s per joule at|; s|/// 1 m; after 100 dB that is 2.447e-5 Pa^2 s per joule.|/// 1 m; after 100 dB that is 2.447007e-5 Pa^2 s per joule.|; s|(source_exposure_1m_pa2s(1.0) - 244_705.0).abs() < 1.0|(source_exposure_1m_pa2s(1.0) - 244_700.7).abs() < 0.1|; s|(received_exposure_pa2s(1.0, 100.0) - 2.447_05e-5).abs() < 1e-9|(received_exposure_pa2s(1.0, 100.0) - 2.447_007e-5).abs() < 1e-11|' $f
grep -n "244_70\|2.447" $f
export HOME=$PWD/../../../.scratchhome CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH CARGO_TARGET_DIR=$PWD/../../../.target
cargo test --offline --release -p mh370-hypotheses 2>&1 | grep -E "test result|FAILED|warning: unused|^warning" | head; cargo clippy --offline --release -p mh370-hypotheses 2>&1 | grep -A5 hydroacoustics | head -20