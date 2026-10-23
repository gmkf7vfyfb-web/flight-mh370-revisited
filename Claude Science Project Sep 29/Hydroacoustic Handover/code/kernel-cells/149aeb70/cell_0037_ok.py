import pandas as pd
P = host.artifact_path
bl = pd.read_csv(P("8698e1e2-a29e-4d6a-b21e-b0c7c965c2eb"))
print(list(bl.columns)); print(bl.head(6).to_string(index=False))
nr = pd.read_csv(P("800a0d39-db21-48e1-acd3-6ec4f3f35543"))
print("\n", list(nr.columns))
