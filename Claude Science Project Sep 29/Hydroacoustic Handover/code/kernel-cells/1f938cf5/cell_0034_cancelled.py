
Z=np.load('L_rows.npz'); keys=list(Z['keys']); cols=list(Z['cols'])
frames=[]
for ii,k in enumerate(keys):
    r=Z[f'r{ii}']
    if r.shape[0]==0: continue
    df=pd.DataFrame(r,columns=cols); df['seed_key']=k; df['stratum']=k.rsplit('/',1)[0]; df['seed_wsum']=Z['wsum'][ii]; df['seed_n']=Z['n'][ii]
    frames.append(df)
L=pd.concat(frames,ignore_index=True)
print(len(L), L.groupby('stratum').size().to_dict())
geo=[Gd.Inverse(*H01W,a,b) for a,b in zip(L.latitude_deg,L.longitude_deg)]
L['rng_km']=[g['s12']/1e3 for g in geo]; L['az']=[(g['azi1'])%360 for g in geo]
L['dCX']=[Gd.Inverse(*CX,a,b)['s12']/1e3 for a,b in zip(L.latitude_deg,L.longitude_deg)]
L['dHX']=[Gd.Inverse(*HX,a,b)['s12']/1e3 for a,b in zip(L.latitude_deg,L.longitude_deg)]
L['in_strip']=(L.rng_km>=R7-60)&(L.rng_km<=R7+250)&(abs(L.az-AZ)<=1.0)
for r_ in (50,100,200,400):
    L[f'CX{r_}']=L.dCX<=r_; L[f'HX{r_}']=L.dHX<=r_
print(L[['in_strip','CX50','CX100','CX200','HX50','HX100','HX200']].sum().to_dict())
print(L.groupby('stratum')[['in_strip','CX50','HX50','CX100']].sum())
print('min dHX',L.dHX.min(),'min dCX',L.dCX.min())
