
for a,b in [("3315","3376"),("3275","3274")]:
    TA=EM.tl_for_rows(lat,a,lats,tab,delta); TB=EM.tl_for_rows(lat,b,lats,tab,delta)
    print(a,b,"median TL per band", np.nanmedian(TA,0).round(1), np.nanmedian(TB,0).round(1))
    print("  grid passA only:", np.nanmedian(tab[a],0).round(1), np.nanmedian(tab[b],0).round(1))
    print("  RAM delta:", delta[a][1].mean(0).round(1), delta[b][1].mean(0).round(1))
