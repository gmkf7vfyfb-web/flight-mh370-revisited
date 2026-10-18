"""Reproduction check before the Ocean Infinity (OI) base re-run (composer, 18 Oct 2026).
(a) The searched-areas combination L = rho + (1-rho) * prod_k (1 - q_k f_k c_k), rho 0.05, reproduces the module's own
    seabed-lnL.npy for run D-he and its OI variants (next-run-d-he-oi2018, -oi2025) from their raw coverage columns.
(b) The decoded coverage rasters give the documented areas (OI 2018 126,009 km2; OI 2025-26 outboard band 9,696.9 km2).
Usage: python check_oi_reproduction.py  (run from the workspace that holds repo/ and with the exchange at X)."""
import pathlib, importlib.util, glob, json, numpy as np
R = pathlib.Path(__file__).resolve().parents[2]            # 'Claude Science Project Sep 29'
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
spec = importlib.util.spec_from_file_location('sl', str(R/'results/composer-pass1-run-c/seabed_loglik.py'))
SL = importlib.util.module_from_spec(spec); spec.loader.exec_module(SL)
COV = R/'engine/hypotheses/seabed-search/coverage'
def area_km2(Rr):
    south, west, step, rows, cols, v = Rr; R_KM = 6371.0072
    lat = lambda k: np.radians(south + k*step)
    return float(sum(R_KM**2*np.radians(step)*(np.sin(lat(r+1))-np.sin(lat(r)))*v[r].astype(float).sum()/255 for r in range(rows)))
out = {'raster_area_km2': {n: round(area_km2(SL.decode(COV/f'{n}.cov')), 1)
                           for n in ['phase2', 'bluefin-2014', 'ocean-infinity-2018', 'ocean-infinity-2025']}}
CAMP = {'oi2018': (0.9, 0.889), 'oi2025': (0.9, 0.7808)}
for var, oname, okey in [('next-run-d-he-oi2018', 'seabed-coverage-ocean-infinity-2018.npy', 'oi2018'),
                         ('next-run-d-he-oi2025', 'seabed-coverage-ocean-infinity-2025.npy', 'oi2025'),
                         ('next-run-d-he', None, None)]:
    mx, n, nz = 0.0, 0, 0
    for sd in sorted(glob.glob(str(X/f'searched-areas/{var}/*/seed-*'))):
        sd = pathlib.Path(sd); lnL = np.load(sd/'seabed-lnL.npy')
        miss = (1-0.945*np.load(sd/'seabed-coverage-phase2.npy').astype(float))*(1-0.9*np.load(sd/'seabed-coverage-bluefin.npy').astype(float))
        if oname:
            co = np.load(sd/oname).astype(float); q, f = CAMP[okey]; miss *= (1-q*f*co); nz += int((co > 0).sum())
        mx = max(mx, float(np.max(np.abs(np.log(0.05+0.95*miss)-lnL)))); n += len(lnL)
    out[var] = dict(rows=n, max_abs_dlnL=mx, rows_with_oi_coverage=nz)
print(json.dumps(out, indent=1))
