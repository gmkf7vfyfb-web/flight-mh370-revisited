cd fix-metz/"Claude Science Project Sep 29"
git -C .. fetch -q origin 2>&1 | grep -v "failed to store"; git -C .. log origin/claude-science-sep29 -5 --format='%h %ad %an | %s' --date=format:%H:%M | cut -c1-170
echo ----; tail -n 45 coordination/architecture.md | head -n 38 | cut -c1-420
echo ----; git -C .. show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-metz-f35a-anchor.md" 2>/dev/null | head -n 30 | cut -c1-360