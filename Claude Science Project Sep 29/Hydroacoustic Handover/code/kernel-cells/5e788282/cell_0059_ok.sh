cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('step2_tl.py').read()
old='''        m = se.merge(s.assign(s_m=(s.range_km * 1000).round(-2)), left_on=[se.s_m.round(-2), "depth_m"], right_on=["s_m", "depth_m"], how="inner", suffixes=("_e", "_n"))
        dc = (m.c_m_s - m.c_mean_m_s).dropna()'''
new='''        m = se.merge(s, on=["node", "depth_m"], how="inner")
        dc = (m.c_m_s - m.c_mean_m_s).dropna()'''
assert old in s; open('step2_tl.py','w').write(s.replace(old,new))
E
mkdir -p /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a
cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nohup python "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a/step2_tl.py" /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/step2 "$PWD/tools" 4 > step2.log 2>&1 &
echo started