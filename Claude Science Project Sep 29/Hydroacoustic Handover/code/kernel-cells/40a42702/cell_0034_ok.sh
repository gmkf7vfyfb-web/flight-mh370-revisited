cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='inputs.py'; s=open(p).read()
s=s.replace('seeds = sorted((eof / s).glob("seed-*"), key=lambda p: int(p.name.split("-")[1]))',
 'seeds = sorted([q for q in (eof / s).glob("seed-*") if q.is_dir() and (q / "impacts32.npy").exists()], key=lambda p: int(p.name.split("-")[1]))')
open(p,'w').write(s)
EOF
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nohup python inputs.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs > /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.log 2>&1 &
sleep 45; tail -3 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.log