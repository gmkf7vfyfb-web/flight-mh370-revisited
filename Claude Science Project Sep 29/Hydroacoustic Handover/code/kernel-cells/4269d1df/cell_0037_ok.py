import pandas as pd, numpy as np
R="repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17/"
prof=pd.read_csv(R+"arc-latitude-first-look/arc-latitude-profile.csv")
print(prof.shape); print(prof.columns.tolist()); print(prof.head(3).to_string()[:1500])
