mm=fla<-30; ii=np.where(mm)[0][np.argmin(abs(Dres[mm]))]
print('TDOA root on mean line south of 30S:',fla[ii].round(3),flo[ii].round(3),'resid',Dres[ii].round(2))
sg=np.sign(Dres); print('all sign changes at lat:',fla[np.where(np.diff(sg)!=0)[0]].round(2))
tt_imp=tH-d1/C0; o=np.argsort(tt_imp); cw=np.cumsum(Wm[o]); 
print('posterior H01W-implied impact time 25/50/75%:',[fmt(tt_imp[o][np.searchsorted(cw,q)]-nT0)[:8] for q in (0.25,0.5,0.75)])