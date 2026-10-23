cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
ls; ls run-j-waypoints | head -3; ls -la run-j-waypoints/seed-1/
cat run-j-waypoints/seed-1/COLUMNS.txt | tr '\n' ' '; echo
python - <<'EOF'
import numpy as np, json
sd='run-j-waypoints/seed-1/'
X=np.load(sd+'impacts32.npy',mmap_mode='r'); print(X.shape, X.dtype)
for f in ['tau90_v1.npz','attitude_v1.npz']:
    z=np.load(sd+f); print(f, {k:(z[k].shape, z[k].dtype) for k in z.files})
z=np.load(sd+'attitude_v1.npz'); print('bank_source mean', z['bank_source'].mean(), 'bank_deg q', np.nanquantile(z['bank_deg'],[.05,.5,.95]))
z=np.load(sd+'tau90_v1.npz'); 
cols=open(sd+'COLUMNS.txt').read().split()
ke=np.asarray(X[:,cols.index('kinetic_energy_j')],float); et=z['energy_transferred_j'].astype(float)
ok=np.isfinite(ke)&np.isfinite(et); print('KE vs E_trans: max rel diff', np.nanmax(np.abs(ke[ok]-et[ok])/ke[ok]), 'KE q', np.nanquantile(ke,[.05,.5,.95])/1e9)
m=json.load(open(sd+'run.json')); print(list(m.keys())[:20])
s=np.load('../run-j-supplement/reduced/impacts-ruleB.npz'); print('supp', {k:(s[k].shape,s[k].dtype) for k in s.files})
EOF
ls summary/ | head; ls ../run-j-supplement/reduced/
df -k /System/Volumes/Data | tail -1