print("terminal.handoff:", cfg["terminal"]["handoff"], "| handoff_floor:", cfg["terminal"]["handoff_floor"],
      "| children:", cfg["terminal"]["children"], "| within_parent:", cfg["terminal"]["within_parent"])
eta = Y[:,ci["latent:engines_thrusting_at_onset"]]
lab = {0.0:"none thrusting", 1.0:"one thrusting", 2.0:"both thrusting"}
print("\nengines thrusting at descent onset (held-out weight):")
for v in (0.0,1.0,2.0):
    print(f"  {lab[v]:16s} rows {int((eta==v).sum()):7d}   weight {float(wn[eta==v].sum()/wn.sum()):.4f}")
print("\nby family (held-out weight within family):")
for f_,nm in [(1.0,"A1 uncontrolled"),(2.0,"A2 piloted after FE"),(3.0,"B deliberate")]:
    mk = fam4==f_
    if wn[mk].sum()==0: continue
    print(f"  {nm:22s}", {lab[v]: round(float(wn[mk&(eta==v)].sum()/wn[mk].sum()),4) for v in (0.0,1.0,2.0)})
print("\nflame-out-time columns present:", [c for c in cols if "flameout" in c or "exhaust" in c])
print("any second-engine column:", [c for c in cols if "engine" in c.lower()])
print("\nparents32 col ranges:", [(round(float(np.asarray(P32[:,j]).min()),4), round(float(np.asarray(P32[:,j]).max()),4)) for j in range(4)])
