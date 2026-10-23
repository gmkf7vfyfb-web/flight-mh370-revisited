for k,cd in CANDS.items():
    for r,t in cd['arr']:
        g=s[(s.rx.astype(str)==r)&(s.time_utc==t)][['rx','time_utc','det','band','p','label_searches']]
        if r=='H01W' and len(g)==0: print(k,r,t,'Kadri Table 1 row (not detected by the module on the digitised trace)' if t in t1.time_utc.values else 'none')
        for _,x in g.iterrows(): print(k, x.rx, x.time_utc, x.det, x.band, round(x.p,3), x.label_searches)