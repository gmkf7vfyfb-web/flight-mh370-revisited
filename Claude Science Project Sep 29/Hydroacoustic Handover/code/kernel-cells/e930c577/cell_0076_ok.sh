cd leg; python - <<'E'
s=open('analyse_L.py').read()
s=s.replace('t_imp = cat("t_impact") + 1394232081.0 - DAY0   # impacts32 stores seconds after T0 = 1394232081; e_tr','t_imp = cat("t_impact") + T0_COMPACT - DAY0; e_tr')
s=s.replace('DAY0 = 1394236800.0;','DAY0 = 1394236800.0; T0_COMPACT = float(json.load(open(sys.argv[3]))["T0"]) if len(sys.argv) > 3 else None;')
open('analyse_L.py','w').write(s)
E
python - <<'E'
import numpy as np, json
z=np.load('scan_dev/run-j-waypoints__seed-1.npz'); t=z['t_impact']; f=z['t_flameout']
print(np.nanquantile(t,[0,.5,1]), np.nanquantile(f,[.05,.5,.95]))
m=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json'))
print({k:v for k,v in m.items() if 'T0' in k or 'epoch' in k.lower() or 'time' in k.lower()} if isinstance(m,dict) else '')
print([k for k in m.keys()])
E