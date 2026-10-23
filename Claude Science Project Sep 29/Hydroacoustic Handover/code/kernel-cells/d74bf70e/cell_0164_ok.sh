M="$PWD/repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; AT="$PWD/at"
cd "$M" && PYTHONPATH="$M" AT="$AT" python - <<'EOF'
import numpy as np, kraken_tl as K, os
AT=os.environ["AT"]
H, c, f, zs, zr = 100.0, 1500.0, 50.0, 30.0, 70.0
prof = [(H, np.array([0.0, H]), np.array([c, c]))]
rr = np.array([1.0, 5.0, 20.0, 50.0])
r, tl, nm, dt = K.tl_path("/tmp/kt_ideal", "ideal", f, prof, [0.0], rr, [zs], [zr], dict(bc="R", c_high=1e9), AT, sphere=False)
n = np.arange(1, 8); g=(n-0.5)*np.pi/H; k=np.sqrt((2*np.pi*f/c)**2-g**2)
I = (2*np.pi/(rr*1000))*np.sum(((2/H)*np.sin(g*zs)*np.sin(g*zr))**2/k, )
tla = -10*np.log10(I)
print("modes", nm, "\nTL kraken  ", np.round(tl[0],3), "\nTL analytic", np.round(tla,3), "\nmax|d|", np.max(np.abs(tl[0]-tla)).round(4), "dt", np.round(dt,3))
EOF