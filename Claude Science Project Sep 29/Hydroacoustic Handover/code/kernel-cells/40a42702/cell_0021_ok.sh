cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "import\|lhyd\|band_fraction\|T_EFF\|T_eff\|RHO\|rho_c\|RHOC\|tl_table\|TL_\|_tl(" per_impact_lnl.py | grep -v "^.*#" | head -40
echo ---- stageB map
grep -n "^def \|^[A-Z_]\+ = \|rho\|T_eff\|peak" imos_stageB_map.py | head -50