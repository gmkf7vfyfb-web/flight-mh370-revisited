cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/metz_f35a"
python - <<'E'
s=open('step3_real_arrival.py').read()
s=s.replace('''        w = rng.standard_normal(n + nper)
        f, tk, Z = signal.stft(w, fs=FS, window="hann", nperseg=nper, noverlap=nper - hop, boundary=None, padded=False)''','''        w = rng.standard_normal(n)
        f, tk, Z = signal.stft(w, fs=FS, window="hann", nperseg=nper, noverlap=nper - hop)''')
s=s.replace('''        _, x = signal.istft(Z * np.sqrt(G), fs=FS, window="hann", nperseg=nper, noverlap=nper - hop, boundary=False)''','''        _, x = signal.istft(Z * np.sqrt(G), fs=FS, window="hann", nperseg=nper, noverlap=nper - hop)''')
open('step3_real_arrival.py','w').write(s)
E
python - <<'E'
import sys; sys.path.insert(0,'.')
import step3_real_arrival as S, numpy as np
for el in ("H11N1","H11S1"): S.ART[el]=S.arrival_data(el)
for k in ("R1","R2"):
    for el in ("H11N1","H11S1"):
        te=[]
        for s in range(5):
            x=S.synth(k,el,np.random.default_rng(s)); c=np.cumsum(x**2); te.append((S.RUN.peak_level_db(x)[1], np.searchsorted(c,.05)/100, np.searchsorted(c,.95)/100))
        print(k,el,np.round(np.mean(te,0),2))
E