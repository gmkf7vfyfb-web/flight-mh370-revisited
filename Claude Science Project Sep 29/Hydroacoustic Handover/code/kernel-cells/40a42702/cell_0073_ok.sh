cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='eta_map.py'; s=open(p).read()
s=s.replace('    S = np.load(inputs_dir / "subsample.npz"); inp = json.load(open(inputs_dir / "inputs.json"))',
'''    S0 = np.load(inputs_dir / "subsample.npz"); inp = json.load(open(inputs_dir / "inputs.json"))
    THIN = 8   # declared: a further 1-in-8 systematic thin of the saved subsample for the bisection (run time); ESS reported per option
    S = {k: S0[k][::THIN] for k in S0.files}''')
s=s.replace('    res = {"method": R.PRIMARY_METHOD, "taus": taus, "n_rows": int(n),', '    res = {"method": R.PRIMARY_METHOD, "taus": taus, "n_rows": int(n), "thin": THIN, "ess": {},')
s=s.replace('            key = f"{o}/p{p:g}"; w = weights(o, p)\n', '            key = f"{o}/p{p:g}"; w = weights(o, p); res["ess"][key] = float(1.0 / np.sum(w ** 2))\n')
s=s.replace('        for _ in range(40):', '        for _ in range(28):')
s=s.replace('Usage: python eta_map.py', 'Rows: 1-in-8 systematic thin of subsample.npz (declared; ESS per option reported).\nUsage: python eta_map.py')
open(p,'w').write(s)
EOF
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
OMP_NUM_THREADS=1 python eta_map.py $OUT/inputs $OUT/run $OUT/eta 2>&1 | tail -15