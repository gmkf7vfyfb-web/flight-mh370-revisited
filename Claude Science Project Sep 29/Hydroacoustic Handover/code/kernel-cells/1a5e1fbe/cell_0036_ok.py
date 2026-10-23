d29=df[df.date=='2014-03-29']; print(len(d29), d29.lat.notna().sum(), df.date.value_counts().to_dict())
print(d29[d29.image_id.isin([5832,5833,5846,5847,5853,5854])][['image_id','utc_time','lat','lon','source_note']].to_string())
print(d29.lat.min(),d29.lat.max(),d29.lon.min(),d29.lon.max(), d29.utc_time.min(), d29.utc_time.max())