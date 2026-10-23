
mabs['ratio_rec_to_impact']=mabs['P(recorder detached rests <=2 km)']/mabs['P(impact point <=2 km, no settling)']
mabs['ratio_fus_to_impact']=mabs['P(recorder in aft fuselage rests <=2 km)']/mabs['P(impact point <=2 km, no settling)']
print(mabs.to_string())
cent=strip[strip.dAz_deg==0]; segs=[]
for lo_,hi_ in [(-60,0),(0,50),(50,100),(100,150),(150,200),(200,250)]:
    q=cent[(cent.range_minus_R7_km>=lo_)&(cent.range_minus_R7_km<hi_)]
    allq=strip[(strip.range_minus_R7_km>=lo_)&(strip.range_minus_R7_km<hi_)]
    segs.append(dict(seg=f'{lo_} to {hi_} km',cmin=q.depth_m.min(),cmed=q.depth_m.median(),cmax=q.depth_m.max(),smin=allq.depth_m.min(),smax=allq.depth_m.max(),aus=(allq.source=='AusSeabed150').mean(),tid40=(allq[allq.source!='AusSeabed150'].gebco_tid==40).mean()))
SEG=pd.DataFrame(segs); SEG.to_csv('out/seabed_depth_bearing_strip_summary.csv',index=False); print(SEG.round(2).to_string())
desc=TAB[(TAB.case=='runJ_L')&(TAB.family=='all')][['cls','descent_min_p50','below_p50']]; print(desc.round(1))
