print('separation km', round(GW.inv(flo[i_t],fla[i_t],flo[i_b],fla[i_b])[2]/1000))
t0b=tH-dH[i_b]/C0; print('impact time (H01W, bearing pt)',fmt(t0b-nT0)[:8], ' range km',round(dH[i_b]))
# TDOA gradient along mean line near bearing point, s per degree latitude
j=slice(i_b-200,i_b+200); g=np.polyfit(fla[j],Dres[j],1)[0]; print('TDOA change along line: %.1f s per deg lat'%g)
Wm=res[('t3','arc_tdoa')]['W']; print('posterior impact time (H01W-implied) median', fmt(np.median(tH-d1/C0)-nT0)[:8])