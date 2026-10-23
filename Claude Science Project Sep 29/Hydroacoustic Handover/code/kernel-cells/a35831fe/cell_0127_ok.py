SUM=pd.read_csv('cand/candidates-A-F-summary.csv')
corr={}
for k,cd in CANDS.items():
    mm=(np.abs(LA-cd['lat'])<=1)&(np.abs(LO-cd['lon'])<=1/np.cos(np.radians(cd['lat'])))
    corr[k]=round(float(condH[mm].sum()),3)
SUM['pleiades_cond_mass_1deg']=SUM.cand.map(corr)
SUM['flight_only_mass_1deg']=[round(float((fo_/fo_.sum())[(np.abs(LA-CANDS[k]['lat'])<=1)&(np.abs(LO-CANDS[k]['lon'])<=1/np.cos(np.radians(CANDS[k]['lat'])))].sum()),3) for k in SUM.cand]
SUM.to_csv('cand/candidates-A-F-summary.csv',index=False); print(SUM[['cand','pleiades_cond_mass_1deg','flight_only_mass_1deg']].to_string())