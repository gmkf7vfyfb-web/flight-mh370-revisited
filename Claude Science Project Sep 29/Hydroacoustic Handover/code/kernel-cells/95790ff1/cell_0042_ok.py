dr=pd.read_csv("drive/blackman_receiver_observations.csv")
pd.set_option("display.width",250,"display.max_colwidth",120)
print(dr.shape); print(dr[["campaign_year","source_id","receiver","status","source_receiver_range_km","frequency_band_or_note","notes"]].to_string())