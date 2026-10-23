cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
grep -n "RAM-KRAKEN" charts.py | cut -c1-120
python - <<'EOF'
p='charts.py'; s=open(p).read()
import re
i=s.index('TL = block 2 grid pass A (PROVISIONAL'); j=s.index('calibration error L', i)
s=s[:i]+'TL: IMOS loggers = module RAM-corrected quantile-path table (38.5-31.6 S, clamped beyond); H01W/H08S = block 2 grid pass A (PROVISIONAL, on-arc sources, source 10 m); "\n         f"'+s[j:]
open(p,'w').write(s)
EOF
grep -c "RAM-corrected quantile" charts.py; python -c "import ast;ast.parse(open('charts.py').read());print('ok')"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
python charts.py $OUT/run $OUT/eta $OUT/inputs/inputs.json $OUT/figs 2>&1 | grep -v Warning | tail -2