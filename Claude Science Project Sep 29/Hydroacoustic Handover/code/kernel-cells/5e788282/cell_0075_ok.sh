cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
import sys; sys.path.insert(0,'.')
import step3_real_arrival as S, numpy as np
for el in ("H11N1","H11S1"): S.ART[el]=S.arrival_data(el)
rng=np.random.default_rng(1)
for k in ("R1","R2"):
    for el in ("H11N1","H11S1"):
        x=S.synth(k,el,rng); e=np.convolve(x**2,np.ones(100)/100,'same'); i=np.argmax(e)
        pk,teff=S.RUN.peak_level_db(x)
        c=np.cumsum(x**2); print(k,el,len(x), "peak t",i/100, "5-95%", np.searchsorted(c,.05)/100, np.searchsorted(c,.95)/100, "T_eff", round(teff,2))
E