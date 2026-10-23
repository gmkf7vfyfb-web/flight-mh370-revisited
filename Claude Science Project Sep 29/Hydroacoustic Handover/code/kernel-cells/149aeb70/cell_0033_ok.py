import pandas as pd, json
P = host.artifact_path
print("WINDOWS\n", pd.read_csv(P("a35f69dc-0c37-4e4e-b01f-70510126ae42")).head(20).to_string(index=False))
print("\nBF SWEEP\n", pd.read_csv(P("a3274757-d1b6-4e7e-83ad-b861e80929b1")).to_string(index=False))
print("\nCOINCIDENCE", json.load(open(P("1f4bf506-64f0-4083-b416-9d89c564dbf3"))))
print("\nBITS", json.load(open(P("5c7d68d9-c6a1-461e-b3bb-e1b50a135878"))))
