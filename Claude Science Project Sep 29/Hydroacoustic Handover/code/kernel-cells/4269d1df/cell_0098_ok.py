q=RC2[(RC2.D=='D0')&(RC2.bearing_sd=='0.5 deg')&(RC2.australia.isin(['none','populated (current, ~10x)','populated 3x']))]
print(q.pivot_table(index=['branch','australia','family'],columns='model',values='LLR').round(2).to_string())
print(q[(q.model=='mean')&(q.australia=='none')][['branch','family','family_share_cond','family_share_runJ']].round(3).to_string())
