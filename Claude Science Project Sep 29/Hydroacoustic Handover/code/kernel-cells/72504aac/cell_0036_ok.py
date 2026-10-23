
t1=pd.read_csv(S+'/named/table1_verdicts.csv')
print(t1[['event_id','time_utc','bearing_deg','arc_crossing_lat','arc_crossing_lon','range_km','implied_impact_utc','bearing_verdict','line_to_arc_km']].to_string())
pairs=pd.read_csv(S+'/coincidence/pairs.csv')
pm=pairs[pairs.family=='primary_M1b'].sort_values('max_p')
print(pm.head(8)[['rx_a','rx_b','t_a','det_a','p_a','t_b','det_b','p_b','lag_s','lag_lo_s','lag_hi_s','max_p','n_pairs_obs','p_perm']].to_string())
print(os.path.exists(X+'/hydroacoustics/graphics-2026-10-22/ranked/ranked_pairs.csv'))
