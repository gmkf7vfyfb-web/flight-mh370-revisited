cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('geometry.py').read()
s=s.replace('''        E.append(gs("latent:impact_energy_transferred_j"))
        tq = gs("latent:energy_transfer_tau90_s")
        if not np.isfinite(tq).any() and (sd / "tau90_v1.npz").exists():
            tq = np.load(sd / "tau90_v1.npz")["tau90_s"][idx].astype(float)
        tau.append(tq)''','''        Eq = gs("latent:impact_energy_transferred_j"); tq = gs("latent:energy_transfer_tau90_s")
        if (sd / "tau90_v1.npz").exists():   # the impacts32 columns are NaN; the tau90 sidecar is primary (brief Refresh v2 s1)
            sc = np.load(sd / "tau90_v1.npz")
            if not np.isfinite(Eq).any(): Eq = sc["energy_transferred_j"][idx].astype(float)
            if not np.isfinite(tq).any(): tq = sc["tau90_s"][idx].astype(float)
        E.append(Eq); tau.append(tq)''')
s=s.replace('''    sE = z["latent:impact_energy_transferred_j"][ii].astype(float); stau = np.full(len(ii), np.nan)''',
'''    sE = z["latent:impact_energy_transferred_j"][ii].astype(float); stau = np.full(len(ii), np.nan)
    if not np.isfinite(sE).any():   # supplement: total kinetic energy 0.5 m v^2 (the 'energy transferred' upper anchor)
        sE = 0.5 * z["mass_kg"][ii].astype(float) * (z["velocity_east_mps"][ii].astype(float) ** 2 + z["velocity_north_mps"][ii].astype(float) ** 2 + z["velocity_up_mps"][ii].astype(float) ** 2)''')
open('geometry.py','w').write(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python geometry.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry 2>&1 | tail -1
python -c "
import json;e=json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/energy.json'))
for o in e: print(o, {k:'%.2e'%v for k,v in e[o]['E_j_q'].items()}, e[o]['tau90_s_q'])"