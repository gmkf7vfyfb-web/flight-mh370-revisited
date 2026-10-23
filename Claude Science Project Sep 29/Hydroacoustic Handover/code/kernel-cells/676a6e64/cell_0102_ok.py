p1 = pr.sort_values('rank_lnLR').head(1).T
print(p1.to_string()[:3500])