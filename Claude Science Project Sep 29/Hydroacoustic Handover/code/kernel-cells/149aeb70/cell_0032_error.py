import pandas as pd, json, textwrap
P = host.artifact_path
st = pd.read_csv(P("0ea98f49-cf1c-49e2-811d-4b30ebd7dab2"))
print("STATIONS\n", st.to_string(index=False)[:2500])
print("\nBLOCKAGE\n", pd.read_csv(P("8698e1e2-a29e-4d6a-b21e-b0c7c965c2eb")).to_string(index=False)[:1800])
