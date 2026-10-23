cd repo; export GIT_CONFIG_GLOBAL=/dev/null
P="Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
git show "origin/claude-science-sep29:$P/displacement_hist.py" > ../eof/displacement_hist.py 2>/dev/null
cd ..
grep -n "def \|^SATCOM\|^[A-Z_]* = " eof/displacement_hist.py | head -40
echo ==== constraint_log_factor
python - <<'EOF'
import re
s=open('eof/displacement_hist.py').read()
for fn in ['constraint_log_factor','derived_logliks','option_posteriors']:
    i=s.find('def '+fn); j=s.find('\ndef ',i+1); print(s[i:j][:2500]); print('-----')
EOF
echo ==== compact load
sed -n 1,60p eof/compact_impacts.py
echo ==== module pushover usage
grep -rn "pushover\|dive_p\|p_dive\|--p " hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"/*.py | head -20