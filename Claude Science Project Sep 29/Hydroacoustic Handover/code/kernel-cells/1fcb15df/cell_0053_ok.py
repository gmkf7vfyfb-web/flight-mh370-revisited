
rp["rank_lnLR"]=rp.rank_lnLR.astype(int); rs["rank_lnLR"]=rs.rank_lnLR.astype(int)
print(rp.sort_values("rank_lnLR").head(5)[["rank_lnLR","lnLR","rx_a","t_a","det_a","band_a","p_a","rx_b","t_b","det_b","band_b","p_b","family","lag_s","locus_lat","locus_lon","implied_impact_utc","eta_pd50_all_a005","p_perm","n_pairs_obs"]].to_string())
print(rs.sort_values("rank_lnLR").head(5)[["rank_lnLR","lnLR","rx","time_utc","det","band","p","implied_source","implied_impact_utc","eta_needed","source"]].to_string())
sp = rp[(rp.rx_a=="H01W")&(rp.rx_b=="H08S")&(rp.t_a=="00:52:04")&(rp.t_b=="01:12:49")]; print(sp[["rank_lnLR","lnLR","family","det_a","det_b"]].to_string())
