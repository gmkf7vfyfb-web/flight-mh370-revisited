dur = Y[:,ci["t_impact_s"]] - Y[:,ci["t_onset_s"]]
td  = Y[:,ci["latent:time_descending_s"]]
frac = np.where(dur>0, td/dur, np.nan)
print("descending fraction of onset-to-impact time, held-out weighting:")
print("  q05/25/50/75/95 =", [round(x,4) for x in wq(frac, wn)])
print("  P(fraction < 0.60) =", round(float(wn[np.isfinite(frac)&(frac<0.60)].sum()/wn[np.isfinite(frac)].sum()),4))
print("  P(fraction < 0.90) =", round(float(wn[np.isfinite(frac)&(frac<0.90)].sum()/wn[np.isfinite(frac)].sum()),4))
print("  P(onset-to-impact > 1800 s) =", round(float(wn[dur>1800].sum()/wn.sum()),4))
print("\namong descents lasting > 1800 s from onset:")
m3 = dur>1800
print("  descending fraction q05/50/95 =", [round(x,4) for x in wq(frac[m3], wn[m3])])
print("  non-descending seconds q05/50/95 =", [round(x,1) for x in wq((dur-td)[m3], wn[m3])])
print("\nmax non-descending seconds in file:", round(float(np.nanmax(dur-td)),1))
