import pandas as pd
P = host.artifact_path
tl = pd.read_csv(P("f059f801-880b-414d-97d6-8ad13123181f"))
print("imos_tl cols:", list(tl.columns)); print(tl.head(4).to_string(index=False))
nb = pd.read_csv(P("d017f80b-a776-4925-90dd-ecbd2fb8f186"))
print("\nnoise_bands cols:", list(nb.columns)); print(nb.head(8).to_string(index=False))
