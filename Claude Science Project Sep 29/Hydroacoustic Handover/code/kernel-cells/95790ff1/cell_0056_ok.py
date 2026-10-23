e["jd"]=e["jd"].astype("Int64"); e.to_csv("out/blackman_2003_events.csv",index=False)
print(open("out/blackman_2003_events.csv").read().splitlines()[1][:120])