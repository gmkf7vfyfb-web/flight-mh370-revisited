import json, pandas as pd, numpy as np
w=json.load(open("src/era5_wind.json"))["hourly"]; v=json.load(open("src/era5_wave.json"))["hourly"]
df=pd.DataFrame(w).merge(pd.DataFrame(v),on="time"); df["time"]=pd.to_datetime(df.time)
df.to_csv("src/era5_haixun_2014-04-03_06.csv",index=False)
d=df.set_index("time")
print(d.resample("6h").mean().round(2).to_string())