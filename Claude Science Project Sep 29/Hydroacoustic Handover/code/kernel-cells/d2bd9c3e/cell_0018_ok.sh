cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
python - <<'EOF'
import numpy as np, json, time, glob
t=time.time()
X=np.load('run-j-waypoints/seed-1/impacts32.npy',mmap_mode='r'); print(X.shape, X.dtype, time.time()-t)
cols=open('run-j-waypoints/seed-1/COLUMNS.txt').read().split()
c={n:i for i,n in enumerate(cols)}
t=time.time(); w=np.asarray(X[:,c['weight']]); print('col read',time.time()-t)
t=time.time(); ti=np.asarray(X[:,c['t_impact_s']]); print('col read2',time.time()-t)
print('t range', np.nanmin(ti), np.nanmax(ti), np.isfinite(ti).mean())
for k in ['latent:pushover_eligible','latent:pushover_drawn','latent:pushover_to_surface','latent:inflight_p_breakup_to_m0019b','family4_code']:
    v=np.asarray(X[:,c[k]]); print(k, np.unique(v[np.isfinite(v)])[:6], np.isfinite(v).mean())
pd_=np.asarray(X[:,c['latent:pushover_drawn']]); ps=np.asarray(X[:,c['latent:pushover_to_surface']]); pe=np.asarray(X[:,c['latent:pushover_eligible']])
import collections
print(collections.Counter(zip(pe.astype(int),pd_.astype(int),np.nan_to_num(ps,nan=-1).astype(int))))
m=json.load(open('run-j-waypoints/seed-1/run.json'))
print(list(m.keys()))
print(json.dumps(m['config']['hypotheses']['end-of-flight']['logon'])[:500])
print(m.get('compact'), m.get('thinning'))
tot=0
for s in ['run-j-waypoints','run-j-free','run-j-descent-climb','run-j-repro-radar']:
    sds=sorted(glob.glob(s+'/seed-*/impacts32.npy')); n=sum(np.load(f,mmap_mode='r').shape[0] for f in sds); tot+=n; print(s,len(sds),n)
print(tot)
fe=json.load(open('summary/family-evidence-run-j.json')); print(json.dumps(fe)[:1500])
EOF