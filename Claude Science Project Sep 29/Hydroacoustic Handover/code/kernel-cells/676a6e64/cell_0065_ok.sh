uptime; df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'
cd repo; export GIT_CONFIG_GLOBAL=/dev/null; git fetch -q origin claude-science-sep29
echo "=== new inbox entries for hydro since 20:30Z?"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n '^## 2026-10-2[12]' | tail -4
echo "=== END_OF_FLIGHT replies?"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/END_OF_FLIGHT.md" | grep -n '^## 2026-10-2[12]' | tail -3
echo "=== architecture entries tonight"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" | grep -n '^## 2026-10-22' | cut -c1-150