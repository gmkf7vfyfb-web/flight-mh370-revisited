H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/bin:$PATH DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib python - <<EOF
import sys, numpy as np, pathlib, time
sys.path.insert(0, "$H")
import kraken_tl as K
z=np.array([0,1000,4000.]); c=np.array([1500,1480,1520.])
profiles=[(4000.0,z,c),(4000.0,z,c)]
bot=dict(cp=1650.0, cs=0.0, rho=1.9, ap=0.5)
t=time.time()
out = K.tl_path(pathlib.Path('/tmp/krk/w'), 'u', 20.0, profiles, [0.0, 100.0], np.linspace(1,100,20), [10.0], [1000.0], bot, "$PWD/tools")
rr, tl, nm = out[0], out[1], out[2]
print('modes', nm, 'TL 50 km %.1f, 100 km %.1f dB' % (float(np.interp(50, rr, tl[0,0] if tl.ndim==3 else tl[0])), float((tl[0,0] if tl.ndim==3 else tl[0])[-1])), 'secs %.1f' % (time.time()-t))
EOF