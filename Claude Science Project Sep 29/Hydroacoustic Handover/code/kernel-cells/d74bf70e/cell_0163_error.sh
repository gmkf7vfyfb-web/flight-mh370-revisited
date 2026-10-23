M="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python3 - "$M/kraken_tl.py" <<'EOF'
import sys; p=sys.argv[1]; t=open(p).read()
old = """        lines.append("'A' 0.0")
        lines.append(f"    {depth:.2f} {bottom['cp']:.2f} {bottom.get('cs', 0.0):.2f} {bottom['rho']:.3f} {bottom['ap']:.3f} 0.0 /")
        lines.append(f"1400.0 {bottom['cp']:.2f}")"""
new = """        if bottom.get("bc") == "R":                      # rigid bottom (analytic tests only)
            lines.append("'R' 0.0")
            lines.append(f"1400.0 {bottom['c_high']:.2f}")
        else:
            lines.append("'A' 0.0")
            lines.append(f"    {depth:.2f} {bottom['cp']:.2f} {bottom.get('cs', 0.0):.2f} {bottom['rho']:.3f} {bottom['ap']:.3f} 0.0 /")
            lines.append(f"1400.0 {bottom['cp']:.2f}")"""
assert t.count(old)==1; open(p,'w').write(t.replace(old,new))
EOF
cd "$M" && python - <<'EOF'
import numpy as np, kraken_tl as K, time
AT="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/at"
H, c, f, zs, zr = 100.0, 1500.0, 50.0, 30.0, 70.0
prof = [(H, np.array([0.0, H]), np.array([c, c]))]
rr = np.array([1.0, 5.0, 20.0, 50.0])
r, tl, nm, dt = K.tl_path("/tmp/kt_ideal", "ideal", f, prof, [0.0], rr, [zs], [zr], dict(bc="R", c_high=1e9), AT, sphere=False)
n = np.arange(1, 8); g=(n-0.5)*np.pi/H; k=np.sqrt((2*np.pi*f/c)**2-g**2)
I = (2*np.pi/(rr*1000))*np.sum(((2/H)*np.sin(g*zs)*np.sin(g*zr))**2/k[None,:]*np.ones((len(rr),1)),axis=1)
tla = -10*np.log10(I)
print("modes", nm, "TL kraken", np.round(tl[0],3), "analytic", np.round(tla,3), "max|d|", np.max(np.abs(tl[0]-tla)).round(4), "dt", np.round(dt,3))
EOF