import os, datetime
M = "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
os.makedirs(M+"/prepare", exist_ok=True); os.makedirs(M+"/data", exist_ok=True)
h = hyd[hyd["Channel"]=="EDH"].copy()
# keep the epoch valid on 2014-03-08
h["start"]=pd.to_datetime(h["StartTime"]); h["end"]=pd.to_datetime(h["EndTime"])
t=pd.Timestamp("2014-03-08")
h=h[(h.start<=t)&((h.end.isna())|(h.end>t))]
h=h[h.Station.str.match(r"H(01W|08N|08S|11N|11S)")]
out=pd.DataFrame({"element":h.Station,"triad":h.Station.str[:4],"latitude_deg":h.Latitude,"longitude_deg":h.Longitude,
                  "hydrophone_depth_m":-h.Elevation,"sample_rate_hz":h.SampleRate,"epoch_start":h.StartTime,"sensor":h.SensorDescription.str.strip()})
hdr = ("# IMS hydroacoustic triad elements valid on 2014-03-08, network IM.\n"
       "# Source: FDSN station web service, EarthScope (formerly IRIS DMC), level=channel, channel EDH,\n"
       "#   https://service.earthscope.org/fdsnws/station/1/query?net=IM&sta=H*&level=channel&format=text\n"
       f"#   retrieved {datetime.date.today().isoformat()} by prepare/fetch_stations.py. hydrophone_depth_m = -Elevation (metres below sea level).\n"
       "# H08 epochs in this source begin 2002-01-17: 2001 positions (Blackman air9) must come from UCRL-TR-207323 itself.\n")
with open(M+"/data/stations.csv","w") as f:
    f.write(hdr); out.to_csv(f,index=False,float_format="%.6f")
cent = out.groupby("triad")[["latitude_deg","longitude_deg","hydrophone_depth_m"]].mean()
print(out.to_string(index=False)); print(cent.to_string(float_format="%.6f"))
