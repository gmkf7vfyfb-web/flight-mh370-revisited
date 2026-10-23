
RANK = "/Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked"
print(os.path.exists(RANK))
s1 = ic[["receiver","time_utc","t_unix","detector","band_hz","statistic","p","label","eta_needed"]].copy(); s1["source"]="IMOS raw"
s2 = pc[["receiver","time_utc","t_unix","detector","band_hz","statistic","p","label","eta_needed","p_B","panel"]].copy(); s2["source"]="digitised Kadri Fig. 9 panel "+s2.panel
S = pd.concat([s1,s2], ignore_index=True).sort_values("p")
keep=[]
for _, r in S.iterrows():
    if any((k.receiver==r.receiver) and abs(k.t_unix-r.t_unix)<60 for k in keep): continue
    keep.append(r)
    if len(keep)>=5: break
singles = pd.DataFrame(keep); print(singles[["receiver","time_utc","detector","band_hz","p","label","eta_needed","source"]].to_string())
# pairs: top 5 distinct primary_M1b pairs by max_p
top_pairs = pm.drop_duplicates(["rx_a","rx_b","t_a","t_b"]).head(5)
print(top_pairs[["rx_a","t_a","p_a","rx_b","t_b","p_b","lag_s","lag_lo_s","lag_hi_s","max_p","n_pairs_obs","p_perm"]].to_string())
