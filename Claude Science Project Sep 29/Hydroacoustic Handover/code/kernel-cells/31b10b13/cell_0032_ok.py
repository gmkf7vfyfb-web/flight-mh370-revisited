
ANOTE="provisional - from Brown 2026's quote of Metz 2023; re-derivation from Metz pending"
T=TR.copy()
T["eta_x_F35A"]=T.eta_pd50_all_a005/ANCH; T["eta_level_x_F35A"]=T.eta_level_locus/ANCH
T["rank_lnLR"]=T.lnLR.rank(ascending=False,method="min").astype(int); T["rank_p"]=T.max_p.rank(method="min").astype(int)
T["label_searches"]=[label_of(x) for x in T.max_p]
T["kernel_source"]=[f"{-a:.2f}S {b:.2f}E {hms(c)}" if np.isfinite(a) else "" for a,b,c in zip(T.get("src_lat"),T.get("src_lon"),T.get("src_t"))]
T.loc[T.blocked==True,"caveats"]="contains Scott Reef 3250 (blocked path, no P_D fit): no impact can produce it; ln LR = -inf; C1; C2"
T["F35A_anchor"]=ANOTE; T["status"]="EXPLORATORY; PREDICTIVE, NOT CALIBRATED"
cols_t=["rank_lnLR","lnLR","rank_p","rxs","times","dets","bands","ps","pBs","max_p","label_searches","lags","ln_ftime","ln_f_amp_given_time","lnB","lnLR_D2","lnLR_D3","lnLR_D4",
        "locus_lat","locus_lon","implied_impact_utc","implied_vs_0019","locus_D0_mass_within_1deg","n_arc_loci","other_loci","locus_baz_H01W","kernel_source",
        "eta_pd50_all_a005","eta_x_F35A","eta_level_locus","eta_level_x_F35A","F35A_anchor","eta_post_med","bearing_consistency","cids","n_rows","caveats","status"]
T=T.sort_values(["lnLR","max_p"],ascending=[False,True])[cols_t]
T.to_csv(f"{OUTX}/ranked_triples.csv.tmp",index=False); os.replace(f"{OUTX}/ranked_triples.csv.tmp",f"{OUTX}/ranked_triples.csv")
for fn in ["ranked_pairs.csv","ranked_singles.csv"]:
    d=pd.read_csv(f"{OUTX}/{fn}"); 
    if "F35A_anchor" not in d: d.insert(list(d.columns).index("eta_x_F35A")+1,"F35A_anchor",ANOTE)
    d.to_csv(f"{OUTX}/{fn}.tmp",index=False); os.replace(f"{OUTX}/{fn}.tmp",f"{OUTX}/{fn}")
print(len(T), (T.blocked if "blocked" in T else 0), T.groupby("rxs").size().shape, np.isfinite(T.lnLR).sum())
print(T.head(3)[["rank_lnLR","lnLR","rxs","times","eta_x_F35A"]].to_string())
# H01W x H08S x IMOS best, IMOS x IMOS x IMOS best
for pat in ["H01WxH08S","x3376x3274","x3274x3275"]:
    q=T[T.rxs.str.contains(pat)&np.isfinite(T.lnLR)]; print(pat,len(q)); print(q.head(2)[["rank_lnLR","lnLR","rxs","times","ps","eta_x_F35A"]].to_string())
q=T[~T.rxs.str.contains("H0")]; print("IMOSx3", len(q), np.isfinite(q.lnLR).sum()); print(q.head(3)[["rank_lnLR","lnLR","rxs","times","ps"]].to_string())
