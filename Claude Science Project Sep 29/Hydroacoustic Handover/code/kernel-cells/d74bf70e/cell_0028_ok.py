import pandas as pd, io, numpy as np
ch = pd.read_csv("hydro/im_hyd_channels.txt", sep="|")
ch.columns = [c.strip().lstrip("#").strip() for c in ch.columns]
hyd = ch[ch["Station"].str.match(r"H\d\d[NSW]\d") & ~ch["Channel"].str.startswith("L")]
print(hyd[["Station","Channel","Latitude","Longitude","Depth","Elevation","SensorDescription","SampleRate","StartTime","EndTime"]].to_string())
