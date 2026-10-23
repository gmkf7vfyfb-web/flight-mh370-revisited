import pandas as pd
D="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/"
sl = pd.read_csv(D+"blackman_shot_lines.csv", comment="#")
print(sl.columns.tolist())
print(sl[sl.site.astype(str).str.contains("air9|air8")].T.to_string())