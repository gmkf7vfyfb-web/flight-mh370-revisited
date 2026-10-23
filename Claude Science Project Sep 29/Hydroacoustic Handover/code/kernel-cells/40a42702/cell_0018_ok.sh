cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw; ls passA | head; ls passB | head; tail -2 passB.log
cd "$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 1,60p per_impact_lnl.py | cut -c1-200
grep -n "tl_table\|TL_TABLE\|read_csv\|np.load\|def received\|def level\|rho\*c\|rho_c\|ESD\|esd" per_impact_lnl.py | head -40