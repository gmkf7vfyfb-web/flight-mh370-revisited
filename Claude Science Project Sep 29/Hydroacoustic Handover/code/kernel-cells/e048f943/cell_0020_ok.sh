cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
python - <<'EOF'
import numpy as np, json
s=np.load('../run-j-supplement/reduced/impacts-ruleB.npz'); print('supp', {k:(s[k].shape,str(s[k].dtype)) for k in s.files})
print(json.load(open('summary/family-evidence-run-j.json'))['p_core'])
sd='run-j-waypoints/seed-1/'
X=np.load(sd+'impacts32.npy',mmap_mode='r'); cols=open(sd+'COLUMNS.txt').read().split()
Y=np.asarray(X[:200000]); c={k:i for i,k in enumerate(cols)}
ke=0.5*Y[:,c['mass_kg']]*(Y[:,c['velocity_east_mps']]**2+Y[:,c['velocity_north_mps']]**2+Y[:,c['velocity_up_mps']]**2)
z=np.load(sd+'tau90_v1.npz'); et=z['energy_transferred_j'][:200000]
ok=np.isfinite(ke)&np.isfinite(et)&(ke>0); print('KE vs E_trans rel diff q50/q99/max', np.quantile(np.abs(ke[ok]-et[ok])/ke[ok],[.5,.99,1]))
print('arc_distance q', np.nanquantile(Y[:,c['arc_distance_nm']],[.01,.5,.99]), 'lat q', np.nanquantile(Y[:,c['latitude_deg']],[.01,.5,.99]))
EOF
cd "$OLDPWD"; cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
sed -n 235,282p prepare/tl_grid_table.py
head -3 results-data/tl_grid_run_j/ims_tl_kraken_arc.csv; head -3 results-data/tl_grid_run_j/imos_tl_ramcorr_arc.csv
head -5 results-data/kadri_fig9_noise/h01w_panel_b_bands_DIGITISED.csv
head -5 results-data/imos1d/calibration_gain.csv