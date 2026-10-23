M="$PWD/repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; AT="$PWD/at"
python3 - "$M/kraken_tl.py" <<'EOF'
import sys; p=sys.argv[1]; t=open(p).read()
a='def write_env(path, title, freq, profiles, sd, rd, bottom, fg=None):'
b='def write_env(path, title, freq, profiles, sd, rd, bottom, fg=None, pts_per_lambda=15):'
c='        lines.append(f"0 0.0 {depth:.2f}")'
d='        nmesh = max(500, int(pts_per_lambda * depth * freq / min(c)) + 1)   # explicit mesh: the auto mesh was 0.1 dB off in the analytic test\n        lines.append(f"{nmesh} 0.0 {depth:.2f}")'
e='def tl_path(workdir, root, freq, profiles, rprof_km, rr_km, sd, rd, bottom, at_bin, fg=None, sphere=True):'
f='def tl_path(workdir, root, freq, profiles, rprof_km, rr_km, sd, rd, bottom, at_bin, fg=None, sphere=True, pts_per_lambda=15):'
g='    write_env(wd / f"{root}.env", root, freq, profiles, sd, rd, bottom, fg)'
h='    write_env(wd / f"{root}.env", root, freq, profiles, sd, rd, bottom, fg, pts_per_lambda)'
for x,y in [(a,b),(c,d),(e,f),(g,h)]:
    assert t.count(x)==1,x; t=t.replace(x,y)
open(p,'w').write(t)
EOF
cd "$M" && PYTHONPATH="$M" AT="$AT" python - <<'EOF'
import numpy as np, pandas as pd, kraken_tl as K, os, time
AT=os.environ["AT"]
c=pd.read_csv("../data/stub/ssp_air9_H08S.csv"); nd=c[c.node==70].dropna()
z=nd.depth_m.values; cc=nd.c_m_s.values; D=float(z[-1])
prof=[(D, z, cc)]
for f in [10.0, 30.0, 60.0]:
    t0=time.time(); r,tl,nm,dt=K.tl_path("/tmp/kt_time","t",f,prof,[0.0],np.array([100.0]),[10.0],[1376.0],dict(cp=1600,rho=1.8,ap=0.8),AT,fg=dict(T=4,S=34.7,pH=8.0,z_bar=1000))
    print(f, "D", D, "modes", nm, "kraken s", round(dt[0],2), "field s", round(dt[1],3), "TL100km", round(float(tl[0,0]),2))
EOF