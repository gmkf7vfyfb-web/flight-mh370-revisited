
cov=[]
for opt in ['held-out','r600-bto-only','r600-bto-raw-bfo']:
    s_=np.load(f'/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources-0019-{opt}.npz')
    S_=s_['state']; KE_=S_[:,c['kinetic_energy_j']]; m_=S_[:,c['mass_kg']]; v=np.sqrt(2*KE_/m_); g=np.abs(S_[:,c['flight_path_angle_deg']])
    vz=-S_[:,c['latent:impact_vertical_speed_mps']]; tau=S_[:,c['latent:energy_transfer_tau90_s']]
    fr=S_[:,c['latent:breakup_p_fragmented']]
    for lab in ['w_flight','w_H']:
        w_=np.asarray(s_[lab],float); w_/=w_.sum()
        regs={'v<100':v<100,'100-150':(v>=100)&(v<150),'150-200':(v>=150)&(v<200),'200-270':(v>=200)&(v<270),'v>=270':v>=270,
              'gamma<5':g<5,'5-30':(g>=5)&(g<30),'gamma>=30':g>=30}
        for k,mk in regs.items():
            ww=w_[mk]; cov.append((opt,lab,k,int(mk.sum()),float(ww.sum()),float(ww.sum()**2/np.sum(ww**2)) if mk.any() else 0))
cv=pd.DataFrame(cov,columns=['option','weights','region','n_rows','weight','ess'])
print(cv[cv.weights=='w_flight'].pivot_table(index='region',columns='option',values=['n_rows','weight','ess']).round(3).to_string())
print('v range',v.min(),v.max(),'tau90 q',np.nanpercentile(tau,[5,50,95]))
