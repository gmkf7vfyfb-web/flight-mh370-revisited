import pandas as pd, json
P = host.artifact_path
cy = pd.read_csv(P("4a2063f3-6673-49b2-b77a-d052d7977d2a"))
print("h08s_cycles cols:", list(cy.columns)); print(cy.head(5).to_string(index=False)); print("rows", len(cy))
print("\noutliers:"); print(pd.read_csv(P("cfb4a586-b3da-4c1b-80a8-b3ba11ec57b7")).to_string(index=False))
pe = json.load(open(P("2cd20e56-2b56-47e2-8043-30e5a5c39eca")))
print("\npulse_energy keys:", list(pe.keys())[:20])
so = json.load(open(P("34c518d1-b6b4-450e-bf43-9063d6469919")))
print("\nshot_outliers keys:", list(so.keys())[:20])
