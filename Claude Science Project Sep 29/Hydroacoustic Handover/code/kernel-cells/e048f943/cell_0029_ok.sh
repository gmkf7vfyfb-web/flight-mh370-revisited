cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
python - <<'EOF'
import pathlib
p=pathlib.Path('run_j_levels.py'); s=p.read_text()
s=s.replace('''    E = z["latent:impact_energy_transferred_j"].astype(np.float32)
    # tau90 is not in the reduced supplement file''','''    E = z["latent:impact_energy_transferred_j"].astype(np.float32)
    # AMENDMENT 1 (plumbing, before any statistic): latent:impact_energy_transferred_j is NaN in every supplement row, so
    # E = 1/2 m v^2 from mass_kg and the three velocity columns (identical to energy_transferred_j on the strata to 3e-7).
    ke = 0.5 * z["mass_kg"].astype(np.float64) * (z["velocity_east_mps"].astype(np.float64) ** 2 + z["velocity_north_mps"].astype(np.float64) ** 2 + z["velocity_up_mps"].astype(np.float64) ** 2)
    E = np.where(np.isfinite(E), E, ke).astype(np.float32)
    # tau90 is not in the reduced supplement file''')
p.write_text(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
time python run_j_levels.py supplement --out $OUT 2>&1 | tail -2
time python run_j_levels.py draw --out $OUT --seeds run-j-free/seed-1 2>&1 | tail -3
python -c "
import numpy as np, json; z=np.load('$OUT/draws/run-j-free/seed-1.npz'); m=json.loads(str(z['meta'])); print(m['res']['n'], m['res']['alloc'], m['res']['code_revision']); print({k:(v['n_draws'],round(v['share_not_ok'] or 0,4)) for k,v in m['sums'].items()}); print(len(z.files))
s=np.load('$OUT/draws/supplement.npz'); print(len(s['D0/p0.5/idx']), s['D0/p0.5/E'][:3]/1e9, s['D0/p0.5/lat'][:3])"
du -sh $OUT