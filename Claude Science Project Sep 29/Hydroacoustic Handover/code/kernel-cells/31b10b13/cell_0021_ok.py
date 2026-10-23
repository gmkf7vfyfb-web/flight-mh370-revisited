
M0=Cm.Machinery(imos_ramgrid=False)
for rx in R.RECEIVERS_GATED:
    print(rx, [round(float(TT.tl_at(M0.xs, M0.tl[rx][:,j], np.array([P.REF_LAT]))[0]),1) for j in range(len(R.BANDS_HZ))])
b0,_=M0.level_base(np.array([P.REF_LAT]),np.array([P.REF_E_J]),np.array([P.REF_TAU_S])); print({k:round(float(v[0]),2) for k,v in b0.items()})
