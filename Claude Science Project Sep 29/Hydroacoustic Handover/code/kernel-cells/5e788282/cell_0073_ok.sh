cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('obs.py').read()
old='''sys.path.insert(0, str(HERE))
import prereg as R  # noqa: E402
'''
new='''import importlib.util as _ilu
_sp = _ilu.spec_from_file_location("metz_prereg", HERE / "prereg.py"); R = _ilu.module_from_spec(_sp); _sp.loader.exec_module(R)
'''
assert old in s; open('obs.py','w').write(s.replace(old,new))
E
python -c "import sys; sys.path.insert(0,'.'); import obs; print(obs.R.NOISE_EXCL_S)"