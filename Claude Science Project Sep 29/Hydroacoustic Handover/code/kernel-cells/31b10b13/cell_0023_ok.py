
PRS["rank"]=PRS.lnLR.rank(ascending=False,method="min")
q=PRS[(PRS.rx_a=="H01W")&(PRS.t_a=="00:52:04")&(PRS.rx_b=="H08S")]
print(q[["t_a","det_a","t_b","det_b","band_b","p_b","pB_b","lag_s","lnLR","lnLR_pB","ln_ftime","ln_f_amp_given_time","lnB","rank","src_lat","src_lon","eta_post_med","bearings"]].sort_values("lnLR",ascending=False).head(8).to_string())
print(np.isfinite(PRS.lnLR).sum(), (PRS.lnLR>0).sum(), PRS.lnLR.max(), SG.lnLR.max())
