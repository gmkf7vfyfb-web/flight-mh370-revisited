cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'
git sparse-checkout add "/$P/coordination/PLEIADES.md" "/$P/results/hydroacoustics-audit-architecture.md" 2>&1 | grep -v ignore || true
git checkout -q -B fix-sep29 origin/claude-science-sep29 2>&1 | grep -v ignore || true
git log -1 --format='%h' ; grep -n "closed access" "$P/coordination/PLEIADES.md" | cut -c1-80; sed -n '206p' "$P/results/hydroacoustics-audit-architecture.md" | cut -c1-260