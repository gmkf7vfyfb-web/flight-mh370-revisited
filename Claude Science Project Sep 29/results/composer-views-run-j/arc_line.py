"""The 7th arc as a line, from run J itself: aircraft positions at 00:19:29 (latent:last_burst_latitude/longitude_deg) of rows whose
R600 BTO residual (bto_residual_us:m0019a) is below 20 us in magnitude (1 us of BTO is about 0.15 km of range), from two seeds of
each production stratum. Longitude per 0.1 deg of latitude = median of those positions (unweighted); bins with < 20 positions are
interpolated. Output arc-line.npz (lat, lon, n). Usage: python arc_line.py OUT.npz"""
import sys, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
sys.path.insert(0, str(PROJ / 'engine/hypotheses/end-of-flight/smoke'))
from compact_impacts import load
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j')
la_all, lo_all = [], []
for st in ('run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb'):
    for k in (1, 2):
        meta, g = load(X / st / f'seed-{k}')
        r = np.asarray(g('bto_residual_us:m0019a')); la = np.asarray(g('latent:last_burst_latitude_deg')); lo = np.asarray(g('latent:last_burst_longitude_deg'))
        ok = np.isfinite(r) & np.isfinite(la) & np.isfinite(lo) & (np.abs(r) < 20)
        la_all.append(la[ok]); lo_all.append(lo[ok]); print(st, k, int(ok.sum()), flush=True)
la, lo = np.concatenate(la_all), np.concatenate(lo_all)
edges = np.arange(-50.0, -5.95, 0.1); mid = 0.5 * (edges[1:] + edges[:-1]); idx = np.digitize(la, edges) - 1
med = np.full(len(mid), np.nan); n = np.bincount(np.clip(idx, 0, len(mid) - 1), minlength=len(mid))
for i in range(len(mid)):
    if n[i] >= 20:
        med[i] = np.median(lo[idx == i])
ok = np.isfinite(med); lon = np.interp(mid, mid[ok], med[ok])
# the arc is a small circle about (nearly) the sub-satellite point: fit centre and angular radius to the binned medians
from scipy.optimize import least_squares
def gc(la1, lo1, la2, lo2):
    a = np.radians; return np.degrees(np.arccos(np.clip(np.sin(a(la1)) * np.sin(a(la2)) + np.cos(a(la1)) * np.cos(a(la2)) * np.cos(a(lo2 - lo1)), -1, 1)))
fit = least_squares(lambda x: gc(x[0], x[1], mid[ok], med[ok]) - x[2], [0.5, 64.5, 50.0])
c_la, c_lo, rad = fit.x; resid_km = fit.fun * 111.2
def lon_on_circle(la):
    a = np.radians; cosr = (np.cos(a(rad)) - np.sin(a(la)) * np.sin(a(c_la))) / (np.cos(a(la)) * np.cos(a(c_la)))
    return c_lo + np.degrees(np.arccos(np.clip(cosr, -1, 1)))          # eastern branch
lon_fit = lon_on_circle(mid)
np.savez(sys.argv[1], lat=mid, lon=lon_fit, lon_median=np.where(ok, med, np.nan), n=n, centre=[c_la, c_lo], radius_deg=rad,
         lat_range_measured=[float(mid[ok].min()), float(mid[ok].max())], fit_rms_km=float(np.sqrt(np.mean(resid_km ** 2))))
print('centre', round(c_la, 3), round(c_lo, 3), 'radius deg', round(rad, 3), 'fit rms km', round(float(np.sqrt(np.mean(resid_km ** 2))), 2), 'max', round(float(np.abs(resid_km).max()), 1))
print('measured lat range', mid[ok].min(), mid[ok].max(), 'lon at 45/40/37/35/30/25/20/15/11 S:', [round(float(lon_on_circle(x)), 2) for x in (-45, -40, -37, -35, -30, -25, -20, -15, -11)])
