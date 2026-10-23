
fs=ss[np.isfinite(ss.eta_needed)&np.isfinite(ss.lnLR)]; fp=pp[np.isfinite(pp.eta_pd50_all_a005)&np.isfinite(pp.lnLR)]
print(fs.eta_needed.min(), fs.eta_needed.max(), fp.eta_pd50_all_a005.min(), fp.eta_pd50_all_a005.max(), (np.isinf(pp.eta_pd50_all_a005)&np.isfinite(pp.lnLR)).sum())
print(fs.nsmallest(3,"eta_needed")[["rx","time_utc","det","eta_needed"]].to_string())
