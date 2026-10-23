cd "repo/Claude Science Project Sep 29/engine"
ls crates/geo/src; grep -n -E '^pub fn|^    pub fn|^pub const|^pub struct' crates/geo/src/*.rs | head -40
echo ===; sed -n 1,40p hypotheses/build.rs
echo ===; ls hypotheses/arc-kernel; sed -n 1,30p hypotheses/arc-kernel/run.toml; ls config | head; ls ~/.cargo/bin 2>/dev/null | head; which cargo rustc