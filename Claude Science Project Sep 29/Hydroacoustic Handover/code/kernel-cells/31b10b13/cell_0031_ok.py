
t0=time.time(); trows=[]
pmap={}
for r in PRS.itertuples(): pmap[(r.cid_a,r.cid_b)]=r; pmap[(r.cid_b,r.cid_a)]=r
for trp in tri:
    cs=[dict(CID.loc[x].to_dict(),cid=x) for x in trp]
    # order: IMS first (H01W, H08S) then IMOS by time
    cs=sorted(cs,key=lambda c:({"H01W":0,"H08S":1}.get(c["rx"],2),c["t_unix"]))
    base=dict(rxs="x".join(c["rx"] for c in cs), times=";".join(c["time_utc"] for c in cs), dets=";".join(c["det"] for c in cs), bands=";".join(c["band"] for c in cs),
              ps=";".join(f"{c['p']:.4g}" for c in cs), pBs=";".join("" if not np.isfinite(c["p_B"]) else f"{c['p_B']:.3g}" for c in cs),
              max_p=max(c["p"] for c in cs), cids=" & ".join(c["cid"] for c in cs))
    lags=[]; 
    for x,y in itertools.combinations(cs,2):
        r=pmap[(x["cid"],y["cid"])]; lags.append(f"{r.rx_a}-{r.rx_b} {r.lag_s:.0f} s in [{r.lag_lo_s:.0f},{r.lag_hi_s:.0f}]")
    base["lags"]="; ".join(lags)
    if any(c["rx"]=="3250" for c in cs):
        base.update(lnN=-np.inf,lnB=float(np.sum([np.log(c["p"]/R.WINDOW_S) for c in cs])),blocked=True); trows.append(base); continue
    sc=score_set(cs); base.update(sc); base.update(locus_cols(cs))
    base["caveats"]=" || ".join(f"{c['rx']}: "+cav_single(c) for c in cs)
    base["bearing_consistency"]=bearing_text([c["rx"] for c in cs],[c["t_unix"] for c in cs], base.get("locus_baz_H01W",np.nan))
    trows.append(base)
TR=pd.DataFrame(trows); print(round(time.time()-t0,1), len(TR))
TR["lnLR"]=TR.lnN-TR.lnB
for o in ["D2","D3","D4"]:
    if f"lnN_{o}" in TR: TR[f"lnLR_{o}"]=TR[f"lnN_{o}"]-TR.lnB
TR["ln_f_amp_given_time"]=TR.lnN-TR.ln_ftime
print(TR.sort_values("lnLR",ascending=False)[["rxs","times","dets","ps","lnLR","ln_ftime","lnB","locus_lat","eta_pd50_all_a005"]].head(10).to_string())
