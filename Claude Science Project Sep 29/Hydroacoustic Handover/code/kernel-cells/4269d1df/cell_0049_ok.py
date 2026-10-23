cls=['flaperon','low_exposure_exterior','high_windage_interior']
out=[]
for m,a in SL.items():
    for ri in (0,5):
        s=a[a['rel']==ri]
        for ci in range(3):
            q=s[s['cls']==ci]; 
            for k in (1,3,6):
                lo,la=q['pos'][:,k,0],q['pos'][:,k,1]
                d=hav(rel[ri]['lat'],rel[ri]['lon'],la,lo); dh=hav(HX[0],HX[1],la,lo)
                out.append((m,rel[ri]['point'],cls[ci],tl[k],round(np.nanmedian(d)),round(np.nanmedian(az(rel[ri]['lat'],rel[ri]['lon'],la,lo))),round(float(np.nanmean(dh<110)),4)))
for o in out: print(o)
