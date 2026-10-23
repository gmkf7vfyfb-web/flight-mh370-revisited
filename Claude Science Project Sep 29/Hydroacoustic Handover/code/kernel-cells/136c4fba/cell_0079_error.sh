cd repo && export XDG_CONFIG_HOME=/tmp/xdg
git log --oneline -1 -- "Claude Science Project Sep 29/engine/data/era5-wind-temperature.bin" 2>/dev/null
grep -n "era5" LARGE_FILES.md 2>/dev/null | head -4
ls -la "Claude Science Project Sep 29/engine/data/" 2>/dev/null | head -8
echo "--- my changes touch Rust? ---"; git status --porcelain | grep -c "\.rs"