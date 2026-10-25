import json, glob, pandas as pd
rows = [json.load(open(f)) for f in glob.glob("work/r/*.json")]; df = pd.DataFrame(rows); df.to_csv("out/tl_ram.csv", index=False); print(len(df))
