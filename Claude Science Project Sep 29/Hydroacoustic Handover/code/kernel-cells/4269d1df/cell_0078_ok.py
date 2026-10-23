for m,a in SL.items():
    s=a[a['rel']==0]; p=pos_at_0315(s['pos'],6,7); d=hav(HX[0],HX[1],p[:,1],p[:,0])
    print(m, np.round(np.nanquantile(d,[0.01,0.05,0.5,0.95,0.99])), float(np.nanmean(d<110)))
