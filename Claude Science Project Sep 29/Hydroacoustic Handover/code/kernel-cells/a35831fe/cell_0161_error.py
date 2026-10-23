dH=DA['H01W']; d74=DA['3274']
Dres=(t74-tH)-(d74-dH)/C0
i_t=np.argmin(abs(Dres)); print('TDOA on mean line:',fla[i_t].round(3),flo[i_t].round(3),'resid',Dres[i_t].round(2))
azl,_,_=GW.inv(np.full_like(flo,H1[1]),np.full_like(fla,H1[0]),flo,fla); azl=np.mod(azl,360)
i_b=np.argmin(abs(wrap(azl-BRG))); print('bearing on mean line:',fla[i_b].round(3),flo[i_b].round(3),'module table 35.87 91.45')
sdD=np.sqrt(SP1**2+SP2**2+(k*(d74[i_b]-dH[i_b]))**2)
print('TDOA residual at bearing point',Dres[i_b].round(1),'s; sd',sdD.round(1),'s; z',(Dres[i_b]/sdD).round(2))
print('separation km', (GW.inv(flo[i_t],fla[i_t],flo[i_b],fla[i_b])[2]/1000).round(0))
t0b=tH-dH[i_b]/C0; print('impact time from H01W at bearing pt',fmt(t0b-nT0) if t0b>1e9 else fmt(t0b))