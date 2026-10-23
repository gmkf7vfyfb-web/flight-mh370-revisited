
sys.path.insert(0,AUD+"scripts"); import air9_audit as AA; importlib.reload(AA)
geo=[(16,12),(24,16),(36,24)]
for Lx,Ly in geo:
    out=[]
    for st in ['H01W','H08S']:
        g=mod[(mod.bottom=='hard')&(mod.station==st)&(mod.src_depth_m==10)].set_index('fc_hz').tl_db
        fb=[f for f in ob[st] if f in g.index]
        r=[ob[st][f]-g[f]+AA.directivity_db(f,0,Lx=Lx,Ly=Ly) for f in fb]
        s=AA.stats(fb,r); out.append((st,round(s['level_median'],1),round(s['slope_db_per_oct'],2)))
    print(Lx,Ly,out, [round(AA.directivity_db(f,0,Lx=Lx,Ly=Ly),1) for f in [10,20,31.5,50,63]])
