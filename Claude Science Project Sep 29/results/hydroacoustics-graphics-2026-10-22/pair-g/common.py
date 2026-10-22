"""Shared geometry, styling and footnotes for the pair-G updates of Pete's seven example charts (22 Oct 2026).
Exec'd into the chart kernel: exec(open('work/common.py').read()). PREDICTIVE, NOT CALIBRATED; caveats C1, C2."""
import numpy as np, pandas as pd, json, os, textwrap, pyproj
import matplotlib as mpl, matplotlib.pyplot as plt
from scipy.interpolate import interp1d
G84 = pyproj.Geod(ellps='WGS84')
X = '/Users/pete/Downloads/mh370-exchange'; S = X + '/hydroacoustics/run-j-searches'
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
RX = json.load(open(S + '/geometry/run.json'))['receivers']
T0 = 1394236800.0

# ---- 7th arc: drawn from the composer's small-circle fit (run J 00:19:29 positions, |BTO residual| < 20 us);
#      loci are solved on the module's TL-grid arc (block 2 pass A, 0.5 deg nodes, cubic), which reproduces G to 0.01 deg.
_a = np.load(X + '/composer/run-j-views/arc-line.npz'); ARC_C = tuple(float(v) for v in _a['centre']); ARC_RAD = float(_a['radius_deg'])
def arc_point_az(az):
    az = np.radians(az); d = np.radians(ARC_RAD); p1, l1 = np.radians(ARC_C[0]), np.radians(ARC_C[1])
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(az))
    l2 = l1 + np.arctan2(np.sin(az) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)
_az = np.linspace(90, 200, 20001); ARC_LAT, ARC_LON = arc_point_az(_az)
_m = (ARC_LAT < 0) & (ARC_LAT > -50) & (ARC_LON > 80); ARC_LAT, ARC_LON = ARC_LAT[_m], ARC_LON[_m]
_tl = pd.read_csv(X + '/hydroacoustics/run-j-tl-grid/tables/tl_grid.csv.gz', usecols=['src_lat', 'src_lon', 'offset_nm'])
_src = _tl[_tl.offset_nm == 0][['src_lat', 'src_lon']].drop_duplicates().sort_values('src_lat')
_f = interp1d(_src.src_lat.values, _src.src_lon.values, kind='cubic')
TL_LAT = np.linspace(_src.src_lat.min(), _src.src_lat.max(), 40001); TL_LON = _f(TL_LAT)

def gdist_km(lat, lon, r):
    la, lo = RX[r]; lat = np.atleast_1d(lat).astype(float); lon = np.atleast_1d(lon).astype(float)
    _, _, d = G84.inv(np.full_like(lat, lo), np.full_like(lat, la), lon, lat); return d / 1000.0
def azimuth(r, lat, lon):
    la, lo = RX[r]; faz, _, d = G84.inv(lo, la, lon, lat); return faz % 360, d / 1000.0
def ray(r, az, dmax_km, n=400):
    la, lo = RX[r]; d = np.linspace(0, dmax_km * 1000, n)
    lon2, lat2, _ = G84.fwd(np.full(n, lo), np.full(n, la), np.full(n, az), d); return lat2, lon2
def path(r, lat, lon, n=200):
    la, lo = RX[r]; pts = G84.npts(lo, la, lon, lat, n)
    return np.array([la] + [p[1] for p in pts] + [lat]), np.array([lo] + [p[0] for p in pts] + [lon])
def locus_from_lag(lag, ra='H01W', rb='H08S', win=(-41.0, -20.0)):
    da = gdist_km(TL_LAT, TL_LON, ra); db = gdist_km(TL_LAT, TL_LON, rb); L = (db - da) / 1.482
    ok = (TL_LAT > win[0]) & (TL_LAT < win[1]); s = np.sign(L - lag)
    idx = np.nonzero(ok[:-1] & ok[1:] & (s[:-1] != s[1:]))[0]
    return [(float(TL_LAT[i]), float(TL_LON[i]), float(da[i])) for i in idx]
def ray_arc_cross(r, az):
    lat, lon = ray(r, az, 5000, 5000)
    # nearest approach of the ray to the drawn arc
    from scipy.spatial import cKDTree
    def xyz(la, lo):
        la, lo = np.radians(la), np.radians(lo); return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
    t = cKDTree(xyz(ARC_LAT, ARC_LON)); d, j = t.query(xyz(lat, lon)); i = int(np.argmin(d))
    return float(lat[i]), float(lon[i]), float(d[i] * 6371.0), float(gdist_km(lat[i], lon[i], r)[0])
def hms(unix): return pd.Timestamp(unix, unit='s').strftime('%H:%M:%S')
def hav(lat, lon, la, lo):
    p1, p2 = np.radians(lat), np.radians(la); dl = np.radians(lo - lon)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))

# ---- the pair (G) and the loci kept from the originals
G = dict(lat=-33.564949768575076, lon=94.50869477928312, t_impact='00:31:41', t_a='00:52:04', t_b='01:12:49', lag=1245)
G_AZ_H01W, G_D_H01W = azimuth('H01W', G['lat'], G['lon']); G_AZ_H08S, G_D_H08S = azimuth('H08S', G['lat'], G['lon'])
T1 = pd.read_csv(S + '/named/table1_verdicts.csv')
def t1row(t, b=None):
    q = T1[T1.time_utc == t]; q = q if b is None else q[np.isclose(q.bearing_deg, b)]; return q.iloc[0]
_A, _B, _D, _R5250 = t1row('00:49:58'), t1row('00:53:31'), t1row('00:54:30', 306.18), t1row('00:52:50')
def _pairlocus(ta, tb):
    lag = (pd.Timestamp('2014-03-08 ' + tb) - pd.Timestamp('2014-03-08 ' + ta)).total_seconds()
    la, lo, d = locus_from_lag(lag)[0]; ti = pd.Timestamp('2014-03-08 ' + ta) - pd.Timedelta(seconds=d / 1.482)
    return dict(lat=la, lon=lo, lag=lag, t_impact=ti.strftime('%H:%M:%S'), d=d)
_E = _pairlocus('00:52:04', '01:10:01'); _F = _pairlocus('00:54:27', '01:12:49')
LOCI = {  # label -> dict(lat, lon, text)
    'A': dict(lat=_A.arc_crossing_lat, lon=_A.arc_crossing_lon, txt=f"A: Cape Leeuwin 00:49:58, {_A.bearing_deg:.2f}°, impact {_A.implied_impact_utc}"),
    'B': dict(lat=_B.arc_crossing_lat, lon=_B.arc_crossing_lon, txt=f"B: Cape Leeuwin 00:53:31, {_B.bearing_deg:.2f}°, impact {_B.implied_impact_utc}"),
    'D': dict(lat=-25.8, lon=101.4, txt="D: Kadri's preferred crossing, 306.18°, impact 00:34:03 (text time) / 00:36:30 (caption time)"),
    'E': dict(lat=_E['lat'], lon=_E['lon'], txt=f"E: Cape Leeuwin 00:52:04 × Diego Garcia 01:10:01, impact {_E['t_impact']}"),
    'F': dict(lat=_F['lat'], lon=_F['lon'], txt=f"F: Cape Leeuwin 00:54:27 × Diego Garcia 01:12:49, impact {_F['t_impact']}"),
    'G': dict(lat=G['lat'], lon=G['lon'], txt="G: Cape Leeuwin 00:52:04 × Diego Garcia 01:12:49, impact 00:31:41"),
}
# ---- colours (focal pair G dominant; comparators lighter)
C_G = '#1b3f8b'; C_KADRI = '#b35806'; C_T1 = '#7b3294'; C_OPEN = '#2b2b2b'; C_BLOCK = '#9a9a9a'; C_CLOUD = '#7f7f7f'
C_LOCI = '#5e5e5e'; C_D = '#b8860b'; C_ARC = '#3a7dbf'

# ---- footnotes
PAIR_TECH = ("Pair G: Cape Leeuwin H01W 00:52:04 UTC (DIGITISED Kadri 2024 Fig. 9 panel c; envelope matched filter M1b p 0.043; Kadri's "
             "'text time 00:52:03', 'caption time 00:54:30') x Diego Garcia South H08S 01:12:49 (DIGITISED panel e, raw, M1b p 0.039; the "
             "airgun-suppressed residual does not keep it, p_B 0.30); lag 1,245 s inside the predicted 809-1,536 s; 19 lag-consistent pairs "
             "vs 8.8 expected, permutation p 0.019 over 36 receiver-pair tests (chance level: a smallest p this low arises about half the time). "
             f"Arc locus 33.6°S 94.5°E, implied impact 00:31:41; eta for P_D(both) = 0.5 is 0.069 = 330x the F-35A anchor 2.1e-4. "
             f"BEARING: the locus lies at {G_AZ_H01W:.1f}° from H01W ({G_D_H01W:,.0f} km) and {G_AZ_H08S:.1f}° from H08S ({G_D_H08S:,.0f} km), WGS84; "
             "Kadri gives 57° (text p. 9) or 306.18° (Table 1 caption) for the 00:52 signal; neither is within 37° of the locus bearing; "
             "nearest Table 1 row 00:52:50 at 274.84° (46 s later).")
PAIR_STE = ("The two sounds (Cape Leeuwin 00:52:04, Diego Garcia 01:12:49) have a time difference that agrees with one point on the arc, 33.6°S 94.5°E. "
            "Pairs like this occur by chance: the test gives p 0.019 from 36 tests, which is a chance level. The Diego Garcia sound is not "
            "kept when the airgun noise is removed. The sound direction that Kadri published for 00:52 does not point to this place. "
            "The impact would need about 330 times more sound than the calibration crash gives.")
COMMON_TECH = ("Source posterior run J, 00:19 Held Out (D0'), dive probability p 0.5; PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation "
               "slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta swept over four "
               "decades, F-35A upper anchor). Module branch hypothesis/hydroacoustics 9b27786; searches results-data/searches_run_j.")
def footnotes(fig, ste, tech, y=0.005, width=210, fs=6.0, gap=0.004):
    t1 = textwrap.fill('(i) ' + ste, width); t2 = textwrap.fill('(ii) ' + tech, int(width * 1.12))
    a = fig.text(0.012, y, t2, ha='left', va='bottom', fontsize=fs - 0.5, color='#333333')
    fig.canvas.draw(); bb = a.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    fig.text(0.012, bb.y1 + gap, t1, ha='left', va='bottom', fontsize=fs, color='#111111')
def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', dpi=200); fig.savefig(f'{OUT}/{name}.pdf')
def bbox_check(fig):
    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    over = [(a.get_text()[:30], b.get_text()[:30]) for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    fb = fig.bbox; out = [t.get_text()[:30] for t, b in texts if b.x0 < fb.x0 - 1 or b.x1 > fb.x1 + 1 or b.y0 < fb.y0 - 1 or b.y1 > fb.y1 + 1]
    return over, out
# land (coarse GEBCO 2026, 0.05 deg)
_g = np.load('work/gebco_coarse.npz'); GEL, GLAT, GLON = _g['EL'], _g['lat'], _g['lon']
def land(ax, extent, color='#e3e3dc'):
    lo0, lo1, la0, la1 = extent; i = (GLAT >= la0 - 1) & (GLAT <= la1 + 1); j = (GLON >= lo0 - 1) & (GLON <= lo1 + 1)
    ax.contourf(GLON[j], GLAT[i], GEL[np.ix_(i, j)], levels=[0, 1e5], colors=[color], zorder=1)
    ax.contour(GLON[j], GLAT[i], GEL[np.ix_(i, j)], levels=[0], colors=['#9e9e94'], linewidths=0.4, zorder=1)
