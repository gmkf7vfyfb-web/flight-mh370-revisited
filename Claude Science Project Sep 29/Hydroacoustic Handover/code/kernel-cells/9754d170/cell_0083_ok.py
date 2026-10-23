
sb=pd.read_csv(AUD+"data/sus_bands.csv")
print(sb[sb.status!='ok'][['shot','station','status']].drop_duplicates().to_string())
pv=sb.pivot_table(index='fc_hz',columns=['shot','station'],values='snr_db').round(1)
print(pv.to_string())
pv2=sb.pivot_table(index='fc_hz',columns=['shot','station'],values='implied_sl_db').round(1); print(pv2.to_string())
