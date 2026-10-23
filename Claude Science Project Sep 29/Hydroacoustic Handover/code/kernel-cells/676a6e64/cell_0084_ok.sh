df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'; uptime
cd repo; export GIT_CONFIG_GLOBAL=/dev/null; git fetch -q origin claude-science-sep29 hypothesis/hydroacoustics 2>/dev/null
echo "=== inbox new?"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n '^## 2026-10-2[12]' | tail -3
echo "=== EoF inbox new?"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/END_OF_FLIGHT.md" | grep -n '^## 2026-10-2[12]' | tail -2
echo "=== tonight's results notes on work branch"; git show origin/claude-science-sep29 --stat --format= | head -0; git ls-tree --name-only origin/claude-science-sep29 "Claude Science Project Sep 29/results/" | grep -E 'hydroacoustics-(weak-signal|run-j|digitised|tl-grid|searches|injection|kadri-package|composition|imos-ram)' | grep -E '\.md$'
echo "=== work-branch hydro commits tonight"; git log --format='%h %s' origin/claude-science-sep29 | grep -i -c hydro
echo "=== architecture entries by hydro tonight"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" | grep -c '^## 2026-10-22.*[Hh]ydro'