import aggregate_flight_leg as A, pandas as pd
r2=dict(r); r2.pop('maps',None); rj2=dict(rj); rj2.pop('maps',None)
t1=pd.DataFrame(A.q1_table([r2],'main',W.KEYS[:6],['all','strip','X200','H200']))
print(t1[['key','region','share','ess','eff_parents','parents_positive','A1_share_in_region','C1_share_in_region']].round(5).to_string())
t2=pd.DataFrame(A.q2_table([r2],'main',W.KEYS[:6],W.VNAME))
print(t2[['key','variant','ln_B_rate','ess_conditional','eff_parents_conditional','cond_share_strip','cond_A2_share','cond_B_share','cond_C1_share']].round(4).to_string())
t3=pd.DataFrame(A.q2_table([rj2],'joined',list(rj2['acoustic']),['T1.0','C1.0'])); print(t3[['key','variant','ln_B_rate','ess_conditional']].round(3))