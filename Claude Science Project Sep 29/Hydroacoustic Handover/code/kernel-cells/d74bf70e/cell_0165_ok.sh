M="$PWD/repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; AT="$PWD/at"
cd /tmp/kt_ideal && for N in 0 500 2000 8000; do sed "s/^0 0.0 100.00/$N 0.0 100.00/" ideal.env > m$N.env; cp ideal.flp m$N.flp; "$AT/Kraken/kraken.exe" m$N >/dev/null 2>&1; "$AT/KrakenField/field.exe" m$N >/dev/null 2>&1
PYTHONPATH="$M" python - $N <<'EOF'
import sys, numpy as np, kraken_tl as K
s=K.read_shd(f"m{sys.argv[1]}.shd"); tl=-20*np.log10(np.abs(s["p"][0,0,0]))
H,c,f,zs,zr=100,1500,50,30,70; n=np.arange(1,8); g=(n-.5)*np.pi/H; k=np.sqrt((2*np.pi*f/c)**2-g**2)
rr=s["rr_m"]; I=(2*np.pi/rr)*np.sum(((2/H)*np.sin(g*zs)*np.sin(g*zr))**2/k); print(sys.argv[1], np.round(tl+10*np.log10(I),4))
EOF
done