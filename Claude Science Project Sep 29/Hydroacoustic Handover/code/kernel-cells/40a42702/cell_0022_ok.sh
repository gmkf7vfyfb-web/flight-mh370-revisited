cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 1,26p imos_stageB_map.py; sed -n 36,48p imos_stageB_map.py; sed -n 70,140p imos_stageB_map.py | grep -n "SE\|tl\|peak\|lev\|snr\|eta\|E_" | head -40
echo ---- per_impact_lnl 100-160
sed -n 100,145p per_impact_lnl.py | cut -c1-220