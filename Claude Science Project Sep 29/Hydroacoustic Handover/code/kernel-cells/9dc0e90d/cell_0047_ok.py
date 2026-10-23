S = eph.loc[eph.epoch_id=='m0019a',['x_km','y_km','z_km']].values[0]
tp = ecef(t.arc_lat.values, t.target_lon.values)
rng = np.linalg.norm(tp - S, axis=1); R0 = np.median(rng); print("range spread km", rng.min()-R0, rng.max()-R0)
from scipy.optimize import brentq
lats = np.arange(-8, -46.01, -0.25); lons=[]
for la in lats:
    g = lambda lo: np.linalg.norm(ecef(la,lo)-S)-R0
    try: lons.append(brentq(g, 70, 125))
    except ValueError: lons.append(np.nan)
arc7 = pd.DataFrame({'lat':lats,'lon':lons}); print(arc7.iloc[::16].to_string())
# check vs track points
print(np.interp(t.arc_lat.values[::-1], lats[::-1], np.array(lons)[::-1]) - t.target_lon.values[::-1])