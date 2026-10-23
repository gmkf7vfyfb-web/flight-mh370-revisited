m = np.isfinite(p2s)
dfp = pd.DataFrame({"par":par[m],"v":p2s[m]})
g = dfp.groupby("par")["v"].agg(["mean","size"])
g = g[g["size"]>=8]
print(f"parents with >=8 push-over draws: {len(g)}, mean draws {g['size'].mean():.1f}")
print("across-parent share of 'to surface': mean %.4f  sd %.4f" % (g["mean"].mean(), g["mean"].std()))
n = g["size"].mean()
print("expected sd if fixed p=0.5 Bernoulli:      %.4f" % np.sqrt(0.25/n))
print("expected sd if per-parent p~U[0,1]:        %.4f" % np.sqrt(1/12 + 0.25/n - (1/12)/n))
print("\nshare of parents with all-0 or all-1 draws: %.4f (fixed p=0.5 would give %.4f)"
      % (float(((g['mean']==0)|(g['mean']==1)).mean()), 2*0.5**n))
