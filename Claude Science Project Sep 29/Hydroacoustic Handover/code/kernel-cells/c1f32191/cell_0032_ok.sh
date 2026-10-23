cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
d=open("driver.py").read()
d=d.replace('''for s in R.STRATA:
    for sd in sorted((R.RUN_J / s).glob("seed-*"), key=lambda p: int(p.name.split("-")[1])):
        if sd.is_dir() and (sd / "impacts32.npy").exists():''','''def seed_dirs(s):
    return sorted([p for p in (R.RUN_J / s).glob("seed-*") if p.is_dir() and (p / "impacts32.npy").exists()], key=lambda p: int(p.name.split("-")[1]))
for s in R.STRATA:
    for sd in seed_dirs(s):
        if True:''')
d=d.replace('''    for sd in sorted((R.RUN_J / s).glob("seed-*"), key=lambda p: int(p.name.split("-")[1])):
        if not sd.is_dir(): continue
        n = np.load''','''    for sd in seed_dirs(s):
        n = np.load''')
open("driver.py","w").write(d); print("ok")
EOF
nohup python driver.py 4 > /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/driver.out 2>&1 &
sleep 30; tail -5 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/driver.log; tail -2 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/driver.out