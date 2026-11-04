"""Evidence ledger, next steps (4 Nov 2026). Usage: python next_steps.py OUTDIR
(1) Indicative split of the satellite result (core) along the 7th arc, from the early-October nested runs endurance_1..4 and the
    timing-only Davey reproduction (davey-bto-only-2026-10-18). Not run J: a guide only.
(2) Synthetic check: staged end-to-end calibration (deskstar, 20-21 Oct 2026; inputs/calib-cases-hist.tgz = hist.json, truth.json,
    case-stats.json per case). Information added by drift + searched areas to core, H(core) - H(all), on 0.25 deg impact-latitude bins,
    for the cases with drift scored by the data-only rule; compared with the real value from the ledger arc masses on the same bins.
    Coverage: HPD level of the true impact latitude per stack."""
import sys, json, glob, tarfile, pathlib
import numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parents[1]; OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
R_E = 3440.065
def H2(m): p = m / m.sum(); q = p[p > 0]; return float(-(q * np.log2(q)).sum())
def hav(a1, o1, a2, o2):
    a1, o1, a2, o2 = map(np.deg2rad, (a1, o1, a2, o2))
    return 2 * np.arcsin(np.sqrt(np.sin((a2 - a1) / 2) ** 2 + np.cos(a1) * np.cos(a2) * np.sin((o2 - o1) / 2) ** 2)) * R_E
# ---- (1) arc geometry: 00:19 arc as a small circle (0.57 N, 64.25 E, radius 44.50 deg), 40.25-19.9 S, 30 NM bins
c_lat, c_lon, rad = np.deg2rad(0.57), np.deg2rad(64.25), np.deg2rad(44.50)
az = np.linspace(0, 2 * np.pi, 200001)
lat = np.arcsin(np.sin(c_lat) * np.cos(rad) + np.cos(c_lat) * np.sin(rad) * np.cos(az))
lon = c_lon + np.arctan2(np.sin(az) * np.sin(rad) * np.cos(c_lat), np.cos(rad) - np.sin(c_lat) * np.sin(lat))
latd, lond = np.rad2deg(lat), np.rad2deg(lon); i = np.where((latd <= -19.9) & (latd >= -40.25) & (lond > 75) & (lond < 115))[0]
latS, lonS = latd[i], lond[i]; o = np.argsort(latS); latS, lonS = latS[o], lonS[o]
sS = np.r_[0, np.cumsum(hav(latS[:-1], lonS[:-1], latS[1:], lonS[1:]))]
BIN = 30.0; edges_s = np.arange(0, sS[-1] + 1e-9, BIN); edges_s = np.r_[edges_s, sS[-1]] if edges_s[-1] < sS[-1] - 1 else edges_s
edges_lat = np.interp(edges_s, sS, latS); widths = np.diff(edges_s)
grid = np.linspace(-50, 50, 2001)
def from_latpdf(p):
    cdf = np.r_[0, np.cumsum(p / p.sum())]; ge = np.r_[grid - 0.025, grid[-1] + 0.025]; return np.diff(np.interp(edges_lat, ge, cdf))
def L90(m):
    p = m / m.sum(); n = np.searchsorted(np.cumsum(np.sort(p)[::-1]), 0.9) + 1; return float(widths[np.argsort(p)[::-1][:n]].sum())
U = widths / widths.sum(); HU = H2(U)
d1 = json.load(open(RES / 'endurance_1_fuel_only/summary.json')); mp = d1['map']; M = np.array(d1['cases'][0]['map'])
clat = mp['lat'][0] + M[:, 0] * mp['step']; clon = mp['lon'][0] + M[:, 1] * mp['step']; w = M[:, 2]
fuel = np.zeros(len(widths)); sub = (np.arange(5) + 0.5) / 5 - 0.5
for dy in sub:
    for dx in sub:
        la = clat + dy * mp['step']; lo = clon + dx * mp['step']
        ring = np.abs(hav(la, lo, 0.57, 64.25) / R_E - rad) <= np.deg2rad(0.25)
        ok = ring & (la <= -19.9) & (la >= -40.25) & (lo > 75)
        fuel += np.histogram(np.interp(la[ok], latS, sS), edges_s, weights=w[ok] / 25)[0]
steps = [('aircraft performance and fuel alone (on the arc)', fuel)]
for r, lab in (('endurance_2_bto_0011', '+ satellite timing to 00:11'), ('endurance_3_btobfo_0011', '+ satellite frequency to 00:11'),
               ('endurance_4_btobfo_0019', '+ 00:19 data')):
    steps.append((lab, from_latpdf(np.array(json.load(open(RES / r / 'summary.json'))['cases'][0]['density']))))
steps.append(('satellite timing alone, all epochs, no fuel model (separate run)',
              from_latpdf(np.array(json.load(open(RES / 'davey-bto-only-2026-10-18/summary-btoonly-mac.json'))['cases'][0]['density']))))
pd.DataFrame([dict(step=lab, bits_along_arc=HU - H2(m), arc90_nm=L90(m)) for lab, m in steps]).to_csv(OUT / 'core-split-indicative.csv', index=False)
# ---- (2) synthetic check
tmp = OUT / '_calib'; tarfile.open(HERE / 'inputs/calib-cases-hist.tgz').extractall(tmp)
E = np.arange(-45.0, 30.01, 0.25); rows = []
def hpdlat(p): q = np.sort(p / p.sum())[::-1]; return (np.searchsorted(np.cumsum(q), 0.9) + 1) * 0.25
for f in sorted(glob.glob(str(tmp / 'case-stats/case-*/hist.json'))):
    cd = pathlib.Path(f).parent; case = int(cd.name.split('-')[-1])
    h = json.load(open(f)); T = json.load(open(cd / 'truth.json')); cs = json.load(open(cd / 'case-stats.json')); P = cs['pooled']
    g = lambda k, q: (P.get(k) or {}).get(q, np.nan); row = dict(case=case, truth_lat=T['impact']['lat'], family=T['family'],
        search_detected=T['search_detected'], drift_scored=cs['drift_rule']['drift_scored'])
    for d in ('D0', 'D1', 'D3', 'D4'):
        pc = np.array(h['cells'][f'{d}|core']['pooled']); pa = np.array(h['cells'][f'{d}|all']['pooled'])
        row[f'{d}_delta_bits_all'] = H2(pc) - H2(pa) if row['drift_scored'] else np.nan
        row[f'{d}_hpd90_lat_core_deg'] = hpdlat(pc)
    for k, st in (('core', 'core'), ('core_searches', 'core+searches'), ('core_drift', 'core+drift'), ('all', 'all')):
        row[f'D0_truth_hpd_level_{k}'] = g(f'D0|{st}', 'hpd_lat')
    rows.append(row)
CAL = pd.DataFrame(rows); CAL.to_csv(OUT / 'synthetic-cases.csv', index=False)
Z = np.load(RES / 'evidence-ledger-v32-2026-11-03/ledger-arc-masses-v32.npz'); real = []
for d in ('D0', 'D1', 'D3', 'D4'):
    bl = Z[f'{d}|lat']
    def tl(sub_):
        m = Z[f'{d}|{sub_}']; ok = np.isfinite(bl) & (m > 0); return np.histogram(bl[ok], E, weights=m[ok])[0]
    pc, pa, ps, pdr = tl('core'), tl('core + drift + search'), tl('core + search'), tl('core + drift')
    real.append(dict(option=d, delta_bits_all=H2(pc) - H2(pa), delta_bits_search=H2(pc) - H2(ps), delta_bits_drift=H2(pc) - H2(pdr),
                     hpd90_lat_core_deg=hpdlat(pc), hpd90_lat_all_deg=hpdlat(pa)))
pd.DataFrame(real).to_csv(OUT / 'real-delta-latitude-bins.csv', index=False)
import shutil; shutil.rmtree(tmp)
print(pd.read_csv(OUT / 'core-split-indicative.csv').round(3).to_string()); print(pd.DataFrame(real).round(3).to_string())
print(CAL[CAL.drift_scored & CAL.case.between(3001, 3030)][['case', 'search_detected', 'D0_delta_bits_all']].round(3).to_string())
