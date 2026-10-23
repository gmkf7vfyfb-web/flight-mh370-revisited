
names = {"H01W":"Cape Leeuwin","H08S":"Diego Garcia South","H08N":"Diego Garcia North","3315":"Perth Canyon 3315","3376":"Perth Canyon 3376",
         "3274":"Portland 3274","3275":"Portland 3275","3250":"Scott Reef 3250","NEAMS":"NEAMS","SWAMS":"SWAMS","SSEIR":"SSEIR","MAD":"MAD","WKER":"WKER","NCRO":"NCRO"}
k=2
for _, r in top_pairs.iterrows():
    if r.rx_a=="H01W" and r.rx_b=="H08S" and r.t_a=="00:52:04" and r.t_b=="01:12:49": continue
    g = add_pair(r, f"Pair {k}: {names[r.rx_a]} {r.t_a} + {names[r.rx_b]} {r.t_b}"); k+=1
    print(g["name"], [(round(a,2),round(b,4)) for a,b in g["loci"]], hms(g["t_imp"]), g["n_ok"], [hms(x) for x in g["win"]["H01W"]])
# singles: condition the run J search-geometry sample on the observed arrival
idx = np.where(okS)[0]; print(len(idx))
sl, so, st, sw = samp["lat"][idx].astype(float), samp["lon"][idx].astype(float), samp["t_unix"][idx].astype(float), samp["w_D0"][idx].astype(float)
SE, STAU = samp["E_j"][idx].astype(float), samp["tau90_s"][idx].astype(float)
t1=time.time(); DS = {rx: dist_km(sl, so, rx) for rx in RXL}; print("dist", round(time.time()-t1,1))
