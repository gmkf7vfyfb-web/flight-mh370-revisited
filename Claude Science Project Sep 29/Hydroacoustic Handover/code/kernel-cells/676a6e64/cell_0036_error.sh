cd /tmp/krk
DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib "$OLDPWD/tools/Kraken/kraken.exe" t 2>&1 | head -12
echo "--- prt"; cat t.prt | head -30
echo "=== use module writer instead"
cd "$OLDPWD"
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/bin:$PATH DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib python - <<EOF
import sys, numpy as np, pathlib
sys.path.insert(0, "$H")
import kraken_tl as K
z=np.array([0,1000,4000.]); c=np.array([1500,1480,1520.])
profiles=[(4000.0,z,c),(4000.0,z,c)]
bot=dict(cp=1650.0, cs=0.0, rho=1.9, ap=0.5)
rr, tl, nm = K.tl_path(pathlib.Path('/tmp/krk/w'), 'u', 20.0, profiles, [0.0, 100.0], np.linspace(1,100,20), [10.0], [1000.0], bot, "$PWD/tools")
print('modes', nm, 'TL at 50 km', float(np.interp(50, rr, tl[0])), 'TL at 100 km', float(tl[0][-1]))
EOF