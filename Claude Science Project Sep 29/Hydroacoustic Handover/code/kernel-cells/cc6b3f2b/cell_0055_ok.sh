cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
s=open("run_kadri.py").read()
s=s.replace("        a = zl[rng.integers(len(zl))]; b = zl[rng.integers(len(zl))]\n",
"        a = zl[rng.integers(len(zl))]; b = np.concatenate([zl[rng.integers(len(zl))], zl[rng.integers(len(zl))]])   # two files give the 491 s lag span\n")
open("run_kadri.py","w").write(s)
EOF
WS=$(cd ../../../../../../..; pwd); export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python run_kadri.py "$WS/out/templates/templates_raw.npz" "$WS/out/kadri" 3 2>&1 | grep -v Warning | tail -3
python run_injection_ext.py "$WS/out/templates/templates_raw.npz" "$WS/out/injection" "$WS/out/injection_ext" 3 2>&1 | grep -v Warning | tail -5