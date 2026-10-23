def summ(W,lab):
    W=W/W.sum(); P=hist_post(W,1.0); im=np.unravel_index(P.argmax(),P.shape)
    print(f"{lab:46s} mean {-np.sum(W*la):.2f} S {np.sum(W*lo):.2f} E | mode {-gla[im[0]]:.2f} S {glo[im[1]]:.2f} E | ESS {1/np.sum(W**2):.0f}")
Lb3=L_bear('t3'); Lb04=L_bear(0.4)
near=(np.abs(la+36)<3)&(np.abs(lo-91)<4)
summ(wi*near,'run J impacts only (box 33-39 S, 87-95 E)')
summ(wi*Lb3,'impacts x bearing (3.3 deg)')
summ(wi*LD,'impacts x time difference')
summ(wi*Lb3*LD,'impacts x bearing x time difference (chart)')
summ(wi*Lb04,'impacts x bearing (0.4 deg)')
summ(wi*Lb04*LD,'impacts x bearing (0.4 deg) x time difference')
# prior density along the bearing line near the star
P0=hist_post(wi,1.0)
for d_km in [-150,-100,-50,0,50,100]:
    lo_,la_,_=GW.fwd(H1[1],H1[0],BRG,2058e3+d_km*1e3)
    i_=np.argmin(abs(gla-la_)); j_=np.argmin(abs(glo-lo_))
    print(f"bearing line {d_km:+4d} km from star: {-la_:.2f} S {lo_:.2f} E prior density rel. {P0[i_,j_]/P0.max():.3f}")
print('star on chart-posterior density, relative to 50% level:', round(P_t3[np.argmin(abs(gla+35.865)),np.argmin(abs(glo-91.472))]/l50,2))