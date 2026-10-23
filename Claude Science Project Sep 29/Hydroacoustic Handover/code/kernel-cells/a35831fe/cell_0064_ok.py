fig.texts[-1].set_text('\n'.join(textwrap.fill(p,165) for p in foot.split('\n')))
fig.savefig('candidates_location_time_coupling.png',dpi=300,bbox_inches='tight')
os.makedirs('review',exist_ok=True)
cols=['id','group','label','receivers','times','bearing','implied_lat','implied_lon','implied_impact','time_test','location_test','prior_mass_1deg','bearing_test','energy_test','known_event','questions','verdict']
R.reindex(columns=cols).to_csv('review/potential-signals-register.csv',index=False)
# Royer cross-ID
X2=X.drop(columns=['tp']).copy()
bb=best[['event','rx','candidate','dt_s','chance_expect','strong']].rename(columns={'candidate':'nearest_candidate','strong':'identified'})
X2=X2.merge(bb,on=['event','rx'],how='left'); X2['identified']=X2.identified.fillna(False)
X2.to_csv('review/royer-events-crossid-all-sites.csv',index=False)
# module candidates flags
sc=s[['rank_lnLR','lnLR','rx','time_utc','det','band','p','implied_source','implied_impact_utc','eta_needed','eta_min','eta_min_xF35A','energy_tier','time_cls','dt_shot']].copy()
sc['royer_flag']=[royer_flag(r,t) for r,t in zip(sc.rx,sc.time_utc)]
sc['receiver_status']=sc.rx.map(lambda r:'no information (North West Shelf in path)' if str(r)=='3250' else ('airgun-dominated digitised panel' if r=='H08S' else 'usable'))
sc.to_csv('review/module-singles-feasibility.csv',index=False)
pcols=['rank_lnLR','lnLR','rank_p','rx_a','t_a','p_a','rx_b','t_b','p_b','lag_s','n_pairs_obs','p_perm','locus_lat','locus_lon','implied_impact_utc','time_cls','loc_mass','loc_cls','eta_level_locus','eta_min','eta_min_xF35A','energy_tier','has_3250','has_H08S','dtshot_a','dtshot_b']
Pc[pcols].to_csv('review/module-pairs-feasibility.csv',index=False)
Tc[['rank_lnLR','lnLR','rxs','times','ps','locus_lat','locus_lon','implied_impact_utc','time_cls','loc_mass','loc_cls','eta_min','eta_min_xF35A','energy_tier','has_3250','has_H08S']].to_csv('review/module-triples-feasibility.csv',index=False)
print(R.verdict.value_counts().to_dict()); print(X2.identified.sum())