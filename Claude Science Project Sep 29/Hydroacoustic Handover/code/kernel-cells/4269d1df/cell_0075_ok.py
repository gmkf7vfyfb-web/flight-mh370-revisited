src=open("repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/kadri_geom.py").read()
ns={}; exec(src.split("out={}")[0], ns)
from scipy.optimize import brentq
arc=[]
for la in np.arange(-34.0,-17.9,0.25):
    f=lambda lo: ns['bto'](la,lo,0.0)-18400.0
    try: arc.append((la,brentq(f,80,115)))
    except Exception: pass
arc=np.array(arc); print(arc[::8])
bl=[ns['pos'](s) for s in np.arange(1300,1900,10)]; bl=np.array(bl)
