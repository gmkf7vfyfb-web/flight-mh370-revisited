
rp = pd.read_csv(f"{RANK}/ranked_pairs.csv", dtype=str); rs = pd.read_csv(f"{RANK}/ranked_singles.csv", dtype=str)
print(rp.shape, rp.columns.tolist()); print(rp.head(6).to_string()[:3000])
print(rs.shape, rs.columns.tolist()); print(rs.head(6).to_string()[:3000])
