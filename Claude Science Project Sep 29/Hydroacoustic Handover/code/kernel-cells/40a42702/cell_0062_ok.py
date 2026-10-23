
p=RUN.pulse(T,2357.2,3.3); pk,_=RUN.peak_level_db(p); t0=time.time()
for lev in [-10,0,10,20]:
    g=10**((lev+bmed-pk)/20); r=RUN.inj_one((1,120.0,g,p,lev,3.3,2357.2,bmed)); print(lev,{k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items() if k not in('file','onset_s','range_km','tau','level_db')})
print(round(time.time()-t0,2),'s for 4 injections')
