cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "S_b\|Sb\|def source\|tau\b" exploratory/pleiades_test/lhyd.py | head -30
echo ----; grep -n "extend\|deepest\|c_mean\|woa" air9_tl_validation.py | head -20