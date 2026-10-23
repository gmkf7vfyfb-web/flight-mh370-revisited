cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
import re
s=open('geometry.py').read()
s=s.replace('SEEDS = [1, 2, 3, 4]','SEEDS = [1, 2, 3, 4, 5, 6, 7, 8]').replace('STRIDE = 16\n','STRIDE = 6\n').replace('SUPP_STRIDE = 8','SUPP_STRIDE = 4')
s=s.replace('seeds 1-4, every 16th row','seeds 1-8, every 6th row').replace('technique >= 1, every 8th row','technique >= 1, every 4th row')
s=s.replace('''                     tau90_s_q=dict(zip(["q5", "q50", "q95"], map(float, wq(TAU[mt], WW[o][mt] / WW[o][mt].sum(), [0.05, 0.5, 0.95])))),''',
'''                     tau90_s_q=(dict(zip(["q5", "q50", "q95"], map(float, wq(TAU[mt], WW[o][mt] / WW[o][mt].sum(), [0.05, 0.5, 0.95])))) if WW[o][mt].sum() > 0 else None),''')
# tau from the tau90 sidecar when the column is NaN
s=s.replace('''        E.append(gs("latent:impact_energy_transferred_j")); tau.append(gs("latent:energy_transfer_tau90_s"))''',
'''        E.append(gs("latent:impact_energy_transferred_j"))
        tq = gs("latent:energy_transfer_tau90_s")
        if not np.isfinite(tq).any() and (sd / "tau90_v1.npz").exists():
            tq = np.load(sd / "tau90_v1.npz")["tau90_s"][idx].astype(float)
        tau.append(tq)''')
open('geometry.py','w').write(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python geometry.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry 2>&1 | tail -3
cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry && python -c "
import json,pandas as pd;e=json.load(open('energy.json'))
for o in e: print(o, 'E50=%.2e'%e[o]['E_j_q']['q50'], e[o]['tau90_s_q'], e[o]['t_impact_q'], 'lat', {k:round(v,2) for k,v in e[o]['lat_q'].items()}, 'ess', round(e[o]['ess']))
l=pd.read_csv('lags.csv'); print(l[l.option=='D0'][['rx_a','rx_b','q0.5','q50','q99.5']].round(0).to_string())"