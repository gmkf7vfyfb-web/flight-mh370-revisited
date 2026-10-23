python3 - <<'EOF'
s=open('rowcond.py').read()
s=s.replace("[:kmax]; K = len(seeds)","; K = len(seeds); lo, hi = (int(x) for x in os.environ.get('SEEDSEL', '0:999').split(':')); seeds = seeds[lo:hi]")
open('rowcond.py','w').write(s)
EOF
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
SEEDSEL=0:12 python rowcond.py rc-wp-a.npz run-j-waypoints=0.9982 > rc-a.log 2>&1 &
SEEDSEL=12:24 python rowcond.py rc-wp-b.npz run-j-waypoints=0.9982 > rc-b.log 2>&1 &
python rowcond.py rc-other.npz run-j-free=0.0013 run-j-repro-radar=0.0003 run-j-descent-climb=0.0002 > rc-c.log 2>&1 &
wait; tail -2 rc-a.log rc-b.log rc-c.log