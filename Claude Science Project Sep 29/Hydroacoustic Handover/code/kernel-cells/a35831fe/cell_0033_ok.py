X.to_csv('royer_crossid_full.csv',index=False)
for _,r in hit.iterrows():
    ms=r.matches.split('; ')
    print(f"ev{r.event}{('/'+r.label) if r.label else ''} {r.cls[:4]} {r.rx} pred {r.pred} ±{r.tol_s} held={r.data_held} n={len(ms)} :: "+' | '.join(m[:70] for m in ms[:4]))