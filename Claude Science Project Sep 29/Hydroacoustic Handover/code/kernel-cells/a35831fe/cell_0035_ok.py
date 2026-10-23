P=pd.read_csv(RK+'ranked_pairs.csv')
cols=['rank_lnLR','lnLR','rank_p','rx_a','t_a','p_a','rx_b','t_b','p_b','lag_s','n_pairs_obs','p_perm','locus_lat','locus_lon','implied_impact_utc','implied_vs_0019','locus_D0_mass_within_1deg','n_arc_loci','eta_pd50_all_a005','eta_level_locus','eta_level_x_F35A','eta_level_ref_a','eta_level_ref_b','bearing_consistency','status']
print(P.sort_values('rank_lnLR')[cols].head(12).to_string())
print(P.sort_values('rank_p')[cols].head(8).to_string())
print(P.eta_level_locus.describe(percentiles=[.01,.05,.1,.5]))
print(P.rx_a.value_counts().to_dict(), P.rx_b.value_counts().to_dict())
print(open(RK+'detectability_and_energy.json').read())