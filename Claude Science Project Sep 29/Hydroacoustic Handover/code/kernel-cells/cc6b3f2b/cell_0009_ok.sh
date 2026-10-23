cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "def load\|polyline\|csv\|Path(" prepare/h08s_shot_outliers.py | head -20
echo ---; grep -rn "figure9\|fig9\|vector-traces\|kadri-figure" prepare/*.py prepare/exploratory/*.py | grep -v "^.*#" | head -10
echo ---; ls data/kadri_package results-data/kadri2a | head -30
export GIT_CONFIG_GLOBAL=/dev/null; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "kadri" | grep -iv "\.py$" | head -30