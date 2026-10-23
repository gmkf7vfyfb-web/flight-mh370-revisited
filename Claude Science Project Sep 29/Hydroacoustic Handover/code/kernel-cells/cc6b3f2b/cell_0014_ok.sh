cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "import lhyd\|lhyd\b" per_impact_lnl.py | head -5
grep -rn "def S_b\|def source_spec\|TAU_GRID\s*=" --include=*.py . ../.. 2>/dev/null | head
echo ---; sed -n 371,470p "../../../../threads/master-prompts/hydroacoustics.md" 2>/dev/null | head -5
sed -n 371,466p "../../../../../repo/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md" 2>/dev/null | head -3
cd /Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/ && ls && cat woa23_95A4_m01.json | head -c 800