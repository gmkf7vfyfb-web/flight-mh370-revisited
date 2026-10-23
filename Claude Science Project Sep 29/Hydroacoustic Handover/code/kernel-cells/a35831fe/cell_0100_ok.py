KD=MODP.replace('/prepare','')+'/data/kadri_fig9_digitised/'
ktr={}
for pnl,st in [('a','H01W'),('b','H01W'),('c','H01W'),('d','H08S'),('e','H08S')]:
    d=pd.read_csv(KD+f'kadri-2024-figure9-panel-{pnl}-{st}.csv')
    t=pd.to_datetime(d.utc).astype('int64')/1e9-T0
    ktr.setdefault(st,[]).append((t.values,d.pressure_pa.values))
for st in ktr: print(st,[ (fmt(t.min()),fmt(t.max()),len(t)) for t,_ in ktr[st]])
rstrip={st:band_series(st) for st in ['H01W2','SSEIR','SWAMS3']}
for st,b in rstrip.items(): print(st, fmt(b.t_utc_s.min()), fmt(b.t_utc_s.max()))
rx_roy={'H01W2':(-34.898071,114.134048),'SSEIR':(-33.51633,70.87617),'SWAMS3':(-42.95883,74.6295)}