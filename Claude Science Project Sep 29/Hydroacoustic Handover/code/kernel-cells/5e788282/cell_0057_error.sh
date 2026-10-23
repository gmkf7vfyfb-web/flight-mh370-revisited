cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
F="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step2_tl.py"
sed -i '' 's/jobs = \[("std", f"f35a-{st}", src0, rc\[st\], at_bin, str(work), str(pathdir))/jobs = [("std", f"f35a-{st}", src0, rc[st], at_bin, str(work), pathdir)/; s/jobs.append(("u2", "f35a-H11S-U2", src0, rc\["H11S"\], at_bin, str(work), str(pathdir)))/jobs.append(("u2", "f35a-H11S-U2", src0, rc["H11S"], at_bin, str(work), pathdir))/; s/jobs.append(("std", f"f35a{dkm:+.0f}km-{st}", s, rc\[st\], at_bin, str(work), str(pathdir)))/jobs.append(("std", f"f35a{dkm:+.0f}km-{st}", s, rc[st], at_bin, str(work), pathdir))/' "$F"
grep -n "pathdir))" "$F"; uptime
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
import sys, time, pathlib; sys.argv=['x']
import step2_tl as S, numpy as np, pandas as pd
S.install_loaders(); rc=S.receivers(); print(rc)
t=time.time(); b,s,info=S.TG.build_path(dict(lat=40.64,lon=142.96), rc['H11S']); print(time.time()-t, info)
e=pd.read_csv(S.EXPORT/"f35a-H11S_bathymetry.csv"); d=-np.interp(e.s_m/1000, b.range_km, b.elevation_m)-e.depth_m
print("depth diff med/p95", np.median(abs(d)), np.quantile(abs(d),.95), "nan c:", s.c_m_s.isna().mean())
se=pd.read_csv(S.EXPORT/"f35a-H11S_soundspeed.csv"); print(se.node.nunique(), s.node.nunique(), se.depth_m.unique()[:5], s.depth_m.unique()[:5])
n0=s[s.node==0]; e0=se[se.node==0]; print(n0[['depth_m','c_m_s']].head(3).values.tolist(), e0[['depth_m','c_mean_m_s']].head(3).values.tolist())
r=S.reference_profile(); print(r.head(3)); 
E