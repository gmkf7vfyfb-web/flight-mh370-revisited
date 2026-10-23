print(cols[-8:])
# strided subsample for coverage analysis
idx = np.arange(0, X.shape[0], 7)          # ~914k rows
Y = np.asarray(X[idx, :], dtype=np.float64)
print("subsample", Y.shape)
w = Y[:, ci["weight"]]
fam = Y[:, ci["family"]]
print("families", np.unique(fam, return_counts=True))
# NaN / constant audit over all columns
rep = []
for c,i in ci.items():
    v = Y[:, i]
    fn = np.isfinite(v)
    rep.append((c, 1-fn.mean(), np.nanmin(v) if fn.any() else np.nan, np.nanmax(v) if fn.any() else np.nan,
                len(np.unique(v[fn])) if fn.any() else 0))
import pandas as pd
R0 = pd.DataFrame(rep, columns=["col","frac_nonfinite","min","max","n_unique"])
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
print(R0[(R0.frac_nonfinite>0.01) | (R0.n_unique<=3)].to_string(index=False))
