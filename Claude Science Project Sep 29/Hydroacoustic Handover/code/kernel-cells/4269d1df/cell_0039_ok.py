mp={'B (pre-registered)':'B','C (pre-registered)':'C','populated only (city+inner=1)':'populated-only (reconstructed)'}
d=[]
for (_,r) in prof[prof.option.isin(mp)].iterrows():
    d.append(r.lnL-float(lnL_at(r.lat,r.lon,r.model,opt=mp[r.option])[0]))
d=np.array(d); print(np.nanmax(np.abs(d)), np.isnan(d).sum(), len(d))
