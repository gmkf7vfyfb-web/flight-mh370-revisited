for nm, mk in [("A-family, ONE engine thrusting at takeover", A & (eta==1.0)),
               ("A-family, NO engines thrusting at takeover", A & (eta==0.0)),
               ("B-family, ONE engine thrusting at onset",   (fam4==3.0) & (eta==1.0))]:
    m2 = mk & np.isfinite(fo)
    print(f"{nm}:  n={int(m2.sum()):7d}  (flameout - takeover) s, q05/50/95 =",
          [round(x,2) for x in wq(fo[m2]-tk[m2], wn[m2], (0.05,0.5,0.95))])
print("\nP(A-family takeover more than 60 s before its flame-out) =",
      float(wn[A & np.isfinite(fo) & (fo-tk > 60)].sum()/wn[A & np.isfinite(fo)].sum()))
