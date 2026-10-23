for o in (0,2000,3000):
    i=np.where(P["offset_m"]==o)[0][0]
    print(o,[f"{P[f'{c}_Pmean'][i]:.2g}" for c in "ACB"])