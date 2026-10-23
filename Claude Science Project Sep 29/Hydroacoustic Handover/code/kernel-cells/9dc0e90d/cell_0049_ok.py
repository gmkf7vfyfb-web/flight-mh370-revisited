c=299792.458; GES=np.array([-2368.8,4881.1,-3342.0]); OFF=499962.0-4283.0
bto=18400.0
path=(bto+OFF)*1e-6*c/2; R_ac = path - np.linalg.norm(S-GES)
print("sat-aircraft range km", R_ac)
lons=[]
for la in lats:
    g=lambda lo: np.linalg.norm(ecef(la,lo,0)-S)-R_ac
    try: lons.append(brentq(g,60,125))
    except ValueError: lons.append(np.nan)
arc7=pd.DataFrame({'lat':lats,'lon':lons}).dropna(); print(arc7.iloc[::16].to_string(), arc7.lat.min())
print("run J median track minus arc (deg lon):", np.round(t.target_lon.values - np.interp(t.arc_lat.values, arc7.lat[::-1], arc7.lon[::-1]),2))