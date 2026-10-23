cd "repo/Claude Science Project Sep 29"
echo "=== ARCHITECTURE.md line 132"; sed -n '132p' ARCHITECTURE.md
echo; echo "=== e2e-calibration-protocol hydro"; grep -n -i -B2 -A4 'hydro' threads/work-orders/e2e-calibration-protocol-2026-10-19.md | cut -c1-350 | head -60
echo; echo "=== hydro module branch recent log"; cd ../..; cd repo; git fetch -q --depth 15 origin hypothesis/hydroacoustics 2>/dev/null; git log --oneline --date=short --format='%h %ad %s' FETCH_HEAD | head -15 | cut -c1-160