cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
p='run_j_windows.py'; s=open(p).read()
s=s.replace('window_start="", window_end="", unconverged="", seed_spread_q0.5_s="", seed_spread_q99.5_s="",',
            'window_start="", window_end="", unconverged="", **{"seed_spread_q0.5_s": "", "seed_spread_q99.5_s": ""},')
open(p,'w').write(s)
EOF
python -m py_compile run_j_windows.py && echo COMPILED
python -c "
import sys; sys.path.insert(0,'.'); import run_j_windows as R
rx=R.receivers(); print(rx); iv=R.held_intervals(); print({k:len(v) for k,v in iv.items()})
import numpy as np
h=np.zeros(R.NBIN); h[1000]=1; print(R.wquant(h,R.QS)[3]-R.GRID0, R.hms(R.GRID0+1000*2+1))
print(R.coverage_fraction(h, [(R.GRID0+1999, R.GRID0+2003)]))
"