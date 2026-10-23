row = pr.sort_values('rank_lnLR').iloc[0]
for k, v in row.items():
    s = str(v)
    print(f"{k}: {s[:160]}")