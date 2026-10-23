cmp_rows=[]
for o,po in (('none','off'),('populated (current, ~10x)','populated only (city+inner=1)')):
    for m in MODELS:
        pr=prof[(prof.model==m)&(prof.option==po)&(prof.position=='median impact')]
        ref=lnE2(P2[('D0','none')],m,OPT2[o])
        llr=pr.lnL-ref; imax=llr.idxmax()
        n=pr[(pr.lat<=-25.99)&(pr.lat>=-33.01)]
        cmp_rows.append(dict(australia=o,model=m,profile_max_LLR=float(llr.max()),profile_max_lat=float(pr.loc[imax,'lat']),
                             profile_LLR_37S=float((pr[pr.lat==-37.0].lnL-ref).iloc[0]),profile_LLR_26_33S_min=float((n.lnL-ref).min()),profile_LLR_26_33S_max=float((n.lnL-ref).max()),
                             crossing_existing=float(ex[(ex.point=='crossing')&(ex.model==m)&(ex.option==('none' if o=='none' else 'populated'))&(ex.D=='D0')].LLR.iloc[0])))
CMP=pd.DataFrame(cmp_rows); print(CMP.round(2).to_string())
os.makedirs('out',exist_ok=True)
RC2.to_csv('out/drift-conditional-llr.csv',index=False)
ex.to_csv('out/drift-point-llr-existing-surfaces.csv',index=False)
fwdf.to_csv('out/forward-drift-L-to-5apr.csv',index=False); fw.to_csv('out/forward-drift-L-snapshots.csv',index=False)
CMP.to_csv('out/drift-arc-profile-comparison.csv',index=False)
bw=[]
for m in SUMB:
    for k,v in SUMB[m].items():
        if isinstance(v,dict): bw.append(dict(model=m,item=k,**v))
pd.DataFrame(bw).to_csv('out/backward-origin-ring-summary.csv',index=False)
# selected-row character table
ch=[]
for D in Ds:
    for v in VARS[1:]:
        pc=P2[(D,v)]; th=pc['thist'].sum(0); di=pc['din'].sum(0); w=pc['sum']
        ch.append(dict(D=D,variant=v,ESS=pc['sum'].sum()**2/pc['sum2'].sum(),t_impact_q05=fmt(wq(tc,th,[0.05])[0]),t_impact_q50=fmt(wq(tc,th,[0.5])[0]),t_impact_q95=fmt(wq(tc,th,[0.95])[0]),
                       range_beyond_arc_km_q05=wq(dc,di,[0.05])[0],range_beyond_arc_km_q50=wq(dc,di,[0.5])[0],range_beyond_arc_km_q95=wq(dc,di,[0.95])[0],
                       lat_mean=float((pc['lat_mean']*w).sum()/w.sum()),lon_mean=float((pc['lon_mean']*w).sum()/w.sum()),rows_99pct_sum_over_seeds=int(pc['rows99'].sum()),parents_99pct_sum_over_seeds=int(pc['parents99'].sum()),
                       share_A1=float(pc['sum_A1'].sum()/w.sum()),share_A2=float(pc['sum_A2'].sum()/w.sum()),share_B=float(pc['sum_B'].sum()/w.sum()),
                       **{f'share_{s}':float(w[pc['strata']==s].sum()/w.sum()) for s in strata_names}))
CH=pd.DataFrame(ch); CH.to_csv('out/selected-rows-character.csv',index=False)
print(CH[CH.variant.isin(['T_core','C_core'])][['D','variant','ESS','t_impact_q50','range_beyond_arc_km_q50','share_A1','share_A2','share_B']].round(3).to_string())
