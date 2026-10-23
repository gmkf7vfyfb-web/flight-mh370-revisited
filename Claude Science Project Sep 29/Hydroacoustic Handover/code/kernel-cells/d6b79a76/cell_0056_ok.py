c2j=[c for c in c2 if c!='cond_C1_share']
print(q2j[c2j].round(3).to_string())
print(q1j[q1j.region.isin(['strip','X50','X200','X400','H200'])][['key','region','share','ess','eff_parents','A1_share_in_region','A2_share_in_region','B_share_in_region','seed_share_se']].round(5).to_string())
# per stratum shares
qs=pd.DataFrame(A.q1_by_stratum(seeds,W.KEYS[:6],['strip','X200']))
print(qs.pivot_table(index=['key','region'],columns='stratum',values='share_within_stratum').round(5).to_string())
print(pd.Series({(r['stratum'],r['seed']):r['min_z2']['T1.0'] for r in seeds}).describe())