import pandas as pd, numpy as np, json
bl = pd.read_csv(host.artifact_path("8698e1e2-a29e-4d6a-b21e-b0c7c965c2eb"))
bl["imp"] = bl["path"].str.split("-").str[0]; bl["rx"] = bl["path"].str.split("-").str[1]
print(bl.pivot_table(index="imp", columns="rx", values=["land_on_track","min_depth_m"]).to_string())
print("\nimpact ids:", sorted(bl['imp'].unique()))
