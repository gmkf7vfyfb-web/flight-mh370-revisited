P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '1,80p' "$P/kadri_predictions.py"
echo ===== LHYD
ls "$P" | head -80
grep -n "def _se\|def _snr0\|def S_b\|def esd\|T_EFF\|def received\|rho\b\|RHO\|1500\|C_WATER" "$P/lhyd.py" 2>/dev/null | head -30