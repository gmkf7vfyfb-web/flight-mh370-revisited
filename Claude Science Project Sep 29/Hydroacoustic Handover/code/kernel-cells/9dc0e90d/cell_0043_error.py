import pandas as pd, json
arc = pd.read_csv("repo/r/Claude Science Project Sep 29/results/drift-runj-2026-10-17/arc-latitude-scan/arclat-release-points.csv")
print(arc.columns.tolist(), len(arc)); print(arc.head(3).to_string())
x = a[0]; print({k:x[k] for k in list(x)[:12]})