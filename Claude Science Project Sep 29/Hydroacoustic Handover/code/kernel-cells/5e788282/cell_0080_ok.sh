cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('step5_pulse.py').read()
old=s[s.index("def profile(step2, st):"):s.index("def one(args):")]
new='''def profile(step2, st):
    """midpoint node profile, extended below the WOA floor with air9_tl_validation.node_profiles (gsw, SA/CT held),
    truncated at the median along-track depth (flat bottom)."""
    import air9_tl_validation as A
    b = pd.read_csv(step2 / "paths" / f"bathy_f35a-{st}.csv"); s = pd.read_csv(step2 / "paths" / f"ssp_f35a-{st}.csv")
    L = float(b.range_km.iloc[-1]); D = float(np.median(-b.elevation_m.values))
    nodes = A.node_profiles(s); node = min(nodes, key=lambda k: abs(nodes[k][0] - L / 2)); _, z, c = nodes[node]
    ok = np.isfinite(c); z, c = z[ok], c[ok]; m = z < D
    return dict(L_km=L, D_m=D, node=int(node), z=np.concatenate([z[m], [D]]), c=np.concatenate([c[m], [np.interp(D, z, c)]]))


'''
s=s.replace(old,new); open('step5_pulse.py','w').write(s)
E
cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nohup python "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step5_pulse.py" $X/step2 $X/at $X/step5 4 > step5.log 2>&1 &
python - <<E
import json
f=json.load(open("$X/step3/step3_fits.json")); m=json.load(open("$X/step3/step3_meta.json"))
for k,v in f.items():
    if '|0.01' in k and ('M1b' in k or 'M0a' in k): print(k, None if v['L50_re_noise_db'] is None else round(v['L50_re_noise_db'],2), round(v['slope_db'],2))
print(json.dumps(m['null_check'])); print(m['seconds'])
E