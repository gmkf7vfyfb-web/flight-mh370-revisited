import numpy as np, json, os
R = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive"
S = f"{R}/next-i-waypoints/seed-1"
cols = [c.strip() for c in open(f"{S}/COLUMNS.txt") if c.strip()]
ci = {c:i for i,c in enumerate(cols)}
X = np.load(f"{S}/impacts32.npy", mmap_mode="r")
print("shape", X.shape, "ncols", len(cols))
term = json.load(open(f"{S}/terminal.json"))
print(json.dumps(term, indent=1)[:2500])
