
ev=pd.read_csv(HB+"data/blackman/blackman_2003_events.csv")
ro=pd.read_csv(HB+"data/blackman/blackman_receiver_observations.csv")
sus=ev[ev.source_type.str.contains('SUS')]
print(sus[['appendixB_event_id','iso_utc','source_depth_m_as_printed','lat_dd','lon_dd','charge_or_source_size','quality_flag','notes']].to_string())
r3=ro[(ro.campaign_year==2003)]
print(r3[['event_id','receiver','analysis','status','predicted_arrival_as_printed_s','observed_arrival_as_printed','band_or_signal_note']].to_string()[:6000])
