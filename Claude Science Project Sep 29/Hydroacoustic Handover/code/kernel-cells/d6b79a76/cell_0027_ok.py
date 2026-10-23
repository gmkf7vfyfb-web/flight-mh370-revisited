import os, sys, time, json, numpy as np
os.chdir('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d6b79a76-addc-42aa-84ad-897b9904c0cb')
sys.path.insert(0,'kh')
import flight_leg_worker as W
EOF='/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j'; CORE='/Users/pete/Downloads/mh370-exchange/core/run-j'
t0=time.time()
r=W.process(('run-j-waypoints',1,0.9982,24,EOF,CORE,'kh/rows_smoke'))
print(time.time()-t0, r['rows'], r['stored_rows'], r['acoustic_keep_rows'])
print(r['geom_rows']); print(r['geom_parents'])
print(r['max_lnL'], r['min_z2'])
k='D0 total q=0.333 (C2 silent)'
P=r['prior'][k]; print({rn:round(np.exp(v['l1']-P['all']['l1']),5) for rn,v in P.items()})
print({vn:v['all']['l1']-P['all']['l1'] for vn,v in r['acoustic'][k].items()})
print(W.XC)