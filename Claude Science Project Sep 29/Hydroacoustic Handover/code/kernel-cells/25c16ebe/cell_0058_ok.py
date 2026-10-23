P32 = np.load(f"{S}/parents32.npy", mmap_mode="r"); print("parents32 shape:", P32.shape)
print("terminal cfg keys:", list(cfg["terminal"].keys()))
print("two_tank_takeover:", cfg["hypotheses"]["end-of-flight"].get("two_tank_takeover"),
      "| fallback_fuel_kg:", cfg["hypotheses"]["end-of-flight"].get("fallback_fuel_kg"))

tk = Y[:,ci["t_takeover_s"]]; fo = Y[:,ci["t_realised_flameout_s"]]; ti = Y[:,ci["t_impact_s"]]
fin = np.isfinite(fo)
wn = P["none"]
print(f"\nflame-out column non-finite (never ran dry before impact): {1-fin.mean():.4f} rows, "
      f"{float(wn[~fin].sum()/wn.sum()):.4f} of held-out weight")
print(f"P(flame-out at/before takeover i.e. already dry when EoF takes over) = {float(wn[fin & (fo<=tk+1)].sum()/wn[fin].sum()):.4f}")
print(f"P(flame-out strictly after takeover, computed inside EoF)            = {float(wn[fin & (fo>tk+1)].sum()/wn[fin].sum()):.4f}")
print("\nflame-out time, held-out weighting:", [hhmm(x) for x in wq(fo, wn)])
print("takeover  time, held-out weighting:", [hhmm(x) for x in wq(tk, wn)])
print("takeover minus flame-out (s), q05..q95:", [round(x,1) for x in wq(tk-fo, wn)])
print("\nP(flame-out before 00:19:29) =", float(wn[fin & (fo<1169.4)].sum()/wn.sum()))
print("P(flame-out between the arcs 00:11-00:19:37) =", float(wn[fin & (fo>=659) & (fo<=1177)].sum()/wn.sum()))
print("P(takeover exactly at hand-off, i.e. dry on arrival) =", float(wn[tk<660].sum()/wn.sum()))
print("\nmass at impact (kg) q05..q95:", [round(x) for x in wq(Y[:,ci['mass_kg']], wn)])
