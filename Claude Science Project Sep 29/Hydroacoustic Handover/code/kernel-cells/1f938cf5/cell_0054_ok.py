
print(TAB[(TAB.cls=='fuselage-section')&(TAB.family!='all')][['case','family','n','p50','p90','p99','floated']].round(2).to_string())
print(TAB[(TAB.cls=='recorder-detached')&(TAB.family!='all')&(TAB.case=='runJ_L')][['case','family','n','p50','p90','p99']].round(2).to_string())
allT=('carry','float','current','glide','ocean-error','diffusion')
rowsH2=rowsH.iloc[:20000]; tr2=np.degrees(np.arctan2(rowsH2.velocity_east_mps.values,rowsH2.velocity_north_mps.values)); fam2=rowsH2['latent:debris_class'].values.astype(int)
terms_tab=[]
for cls in ['recorder-detached','fuselage-section']:
    for off in [None,'carry','float','current','glide','ocean-error','diffusion']:
        tt=tuple(t for t in allT if t!=off)
        o=sm.settle(np.full(20000,HX[0]),np.full(20000,HX[1]),T0+rowsH2.t_impact_s.values,rowsH2.vh.values,tr2,fam2,cls,glorys,wind,np.random.default_rng(7),terms=tt)
        D=np.hypot(*sm.offsets_km(HX[0],HX[1],o['lat'],o['lon']))
        terms_tab.append(dict(cls=cls,term_off=off or 'none (all on)',p50=np.nanpercentile(D,50),p90=np.nanpercentile(D,90),p99=np.nanpercentile(D,99)))
TT=pd.DataFrame(terms_tab); print(TT.round(3).to_string())
