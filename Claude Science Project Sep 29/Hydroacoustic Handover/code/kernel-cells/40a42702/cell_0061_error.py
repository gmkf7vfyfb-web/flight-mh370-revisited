
importlib.reload(RUN)
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection"
T=np.load(f"{OUT}/templates/templates_raw.npz"); tb=json.load(open(f"{OUT}/templates/template_build.json"))
print(tb['n_modes_min'], tb['n_modes_max'], tb['bank']['3376'], tb['bank']['3274']['bank'])
for rx in ['3376','3274','H08S']:
    for tau in [0.11,3.3,10.59]:
        p=RUN.pulse(T, tb['bank'][rx]['bank'][1], tau); pk,te=RUN.peak_level_db(p)
        e=RUN.M.envelope(p,100); print(rx, tau, 'T_eff', round(te,2), 'env peak at', round(np.argmax(e)/10,1), 's; 90% energy span', round((np.cumsum(p**2)/np.sum(p**2)>0.05).argmax()/100,1), round((np.cumsum(p**2)/np.sum(p**2)>0.95).argmax()/100,1))
# smoke: 3 files of 3376, null + one injection
files=RUN.own_14day_files("3376")[:3]; xs=[RUN.C.load_100(f) for f in files]; print([len(x) for x in xs])
bank=RUN.bank_for(T,[float(v) for v in tb['bank']['3376']['bank']],[0.11,3.3,10.59]); RUN._set_bg(xs,bank)
import time; t0=time.time(); nm=RUN.null_one(xs[0]); print({k:(len(v), np.round(np.nanmax(v),3)) for k,v in nm.items()}, round(time.time()-t0,2),'s')
bmed=RUN.level_stats(xs,1,'x')['median']; print('bmed',bmed)
p=RUN.pulse(T,2357.0,3.3); pk,_=RUN.peak_level_db(p); t0=time.time()
for lev in [-10,0,10,20]:
    g=10**((lev+bmed-pk)/20); r=RUN.inj_one((1,120.0,g,p,lev,3.3,2357.0,bmed)); print(lev,{k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items() if k not in('file','onset_s','range_km','tau','level_db')})
print(round(time.time()-t0,2),'s for 4 injections')
