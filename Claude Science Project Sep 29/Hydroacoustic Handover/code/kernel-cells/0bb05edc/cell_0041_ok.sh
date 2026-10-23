cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
echo "=== work order + brief + architecture: Kadri 2019 / JASA / San Juan wording"
git grep -n -i -E "kadri ?\(?2019|kadri2019|JASA" $B -- "$P/threads/work-orders/hydroacoustics-order-2026-10-21.md" "$P/threads/master-prompts/hydroacoustics.md" "$P/coordination/architecture.md" "$P/results/hydroacoustics-digitised-sources.md" "$P/results/hydroacoustics-overnight-2026-10-22-summary.md" "$P/results/hydroacoustics-kadri-package-v2.md" | sed "s|^$B:||" | cut -c1-330 | head -30
echo; echo "=== work order: Metz"
git show $B:"$P/threads/work-orders/hydroacoustics-order-2026-10-21.md" | grep -n -i "metz\|F-35" | cut -c1-330 | head -12
echo; echo "=== commit dates for the 21 Oct brief/work order"
git log -3 --format='%h %ad %an | %s' --date=iso $B -- "$P/threads/work-orders/hydroacoustics-order-2026-10-21.md" | cut -c1-200