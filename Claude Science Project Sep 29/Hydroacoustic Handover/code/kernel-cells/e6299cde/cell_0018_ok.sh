cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 30,48p imos_stageB_map.py
grep -n "def \|rho\|ESD\|esd\|received\|10 \*\* (-\|band_fraction\|eta" per_impact_lnl.py | head -50