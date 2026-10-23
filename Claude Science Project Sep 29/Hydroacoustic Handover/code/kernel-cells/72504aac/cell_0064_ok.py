
RK=pd.read_csv(X+'/hydroacoustics/graphics-2026-10-22/ranked/ranked_pairs.csv')
top=RK.sort_values('rank_lnLR').head(5)
print(top[['rank_lnLR','lnLR','rank_p','rx_a','t_a','det_a','p_a','rx_b','t_b','det_b','p_b','family','locus_lat','locus_lon','implied_impact_utc','status']].to_string())
g=RK[(RK.rx_a=='H01W')&(RK.t_a=='00:52:04')&(RK.rx_b=='H08S')&(RK.t_b=='01:12:49')]
print(g[['rank_lnLR','lnLR','rank_p','det_a','det_b','family','locus_lat','locus_lon','eta_pd50_all_a005','eta_x_F35A','bearing_consistency','status']].to_string())
print(RK.status.value_counts().head())
