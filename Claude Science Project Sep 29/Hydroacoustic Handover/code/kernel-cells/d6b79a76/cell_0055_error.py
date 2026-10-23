q2m=pd.DataFrame(A.q2_table(seeds,'main',W.KEYS,W.VNAME)); q2j=pd.DataFrame(A.q2_table(seeds,'joined',[f'D{d} joined V2' for d in range(5)],W.VNAME))
c2=['key','variant','ln_B_rate','ln_B_single','ess_conditional','eff_parents_conditional','cond_share_strip','cond_share_X200','cond_A1_share','cond_A2_share','cond_B_share','cond_C1_share','seed_lnB_min','seed_lnB_median','seed_lnB_max','seed_B_rel_se']
pd.set_option('display.width',250)
print(q2m[q2m.key.str.contains('total')][c2].round(3).to_string())
print(q2m[~q2m.key.str.contains('total')&q2m.variant.isin(['T1.0','C1.0'])][['key','variant','ln_B_rate','ess_conditional']].round(3).to_string())
print(q2j[c2].round(3).to_string())