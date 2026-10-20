"""Composer views v3 on run J: shared helpers (numpy).

Drift factor (debris finds), per ocean model, at the IMPACT point:
  inside the arc-latitude span of the dedicated run (commit 15ab7c9, 66 points, 26-40 S along the run J D0 median impact track and
  50 NM either side, both ocean models): ln L interpolated linearly in the cross-arc offset over the three points of a latitude
  (held at the end values beyond +/-50 NM) and linearly in arc position between latitudes;
  outside that span: run A rebuilt node surface (views v2 lookup, bilinear in L) plus a per-model offset = mean(dedicated - run A) over
  the 66 points (GLORYS12 -0.673, GlobCurrent -0.881 ln units; measured here), so that both parts are on one scale.
  Options (all from the dedicated run's level alternatives): 'off' = finds only (BASE drift factor); 'B' = pre-registered primary
  Australian non-recovery level (ln_l); 'C' = low level; 'pop' = populated coast only. Australian options are a LABELLED SENSITIVITY.
  Outside 26-40 S the Australian increment (option - off) is held at the value of the nearest end latitude (declared).
  'h100' kernel sensitivity = off + (ln_l_h100 - ln_l) (the run gives h100 under level B only; declared).
Pleiades (conditional on H): joint-surface-rho0.25-gcrel, per ocean model, cell lookup (pleiades/run-j/surfaces, = run I surfaces).
"""
import json, pathlib, sys, zipfile, io
import numpy as np
import pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
V2 = PROJ / 'results/composer-views-run-j'
sys.path.insert(0, str(V2))
import views_common as V   # noqa: E402  (equal-area grid, arc geometry, drift node lookup of v2)
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
LREF = -125.0
ARCLAT = PROJ / 'results/drift-runj-2026-10-17/arc-latitude-scan/results'
MODELS = (('glorys12', 'G'), ('globcurrent', 'C'))
OPTS = ('off', 'B', 'C', 'pop', 'h100')


def arc_sr(lat, lon):
    """(s, r): NM along the 7th arc from its southern tip, and cross-arc offset in NM (positive = farther from the arc centre)."""
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    s = V.arc_s(lat, lon)
    p1, l1 = np.radians(V.ARC_C[0]), np.radians(V.ARC_C[1]); p2, l2 = np.radians(lat), np.radians(lon)
    c = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(l2 - l1)
    dist = np.degrees(np.arccos(np.clip(c, -1, 1)))
    return s, (dist - V.ARC_RAD) * V.NM_R * np.radians(1.0)


def arclat_nodes():
    z = zipfile.ZipFile(ARCLAT / 'arclat-node-tables.zip')
    prof = pd.read_csv(ARCLAT / 'arclat-likelihood-profile.csv')[['node', 'arc_lat', 'position']]
    out = {}
    for mod, tag in MODELS:
        d = pd.concat([pd.read_csv(io.BytesIO(z.read(n))) for n in sorted(z.namelist()) if n.startswith(f'arclat-{mod}-') and n.endswith('nodes.csv')])
        d = d.merge(prof, on='node', how='inner'); assert len(d) == 66, (mod, len(d))
        d['v_off'] = d['ln_l_lev_off']; d['v_B'] = d['ln_l']; d['v_C'] = d['ln_l_lev_C']; d['v_pop'] = d['ln_l_lev_populated']
        d['v_h100'] = d['ln_l_lev_off'] + (d['ln_l_h100'] - d['ln_l'])
        out[tag] = d
    return out


class Drift:
    """Dedicated-run points form an irregular set in (arc position s, cross-arc offset r): the 'perpendicular' triplets are skewed by up
    to 60 NM in s in the south. Interpolation: linear on the Delaunay triangulation of the 66 points in (s, r) [NM, NM]; outside the
    triangulation but inside the s span of the points: nearest point. Outside the s span: run A + offset (see module docstring)."""
    def __init__(self):
        from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
        self.N = np.load(X / 'composer/run-j-views/work/nodes.npz')
        self.nodes = arclat_nodes(); self.offset = {}; self.lin = {}; self.near = {}
        for mod, tag in MODELS:
            d = self.nodes[tag]
            ins, nid, W = V.drift_corners(d.lat_deg.values, d.lon_deg.values)
            LA = np.log(V.drift_lookup(ins, nid, W, np.exp(self.N[f'{mod}_h50'] - LREF))) + LREF
            self.offset[tag] = float(np.nanmean(d.v_off.values - LA))
            s, r = arc_sr(d.lat_deg.values, d.lon_deg.values); P = np.column_stack([s, r])
            Vals = np.column_stack([d[f'v_{o}'].values for o in OPTS])
            self.lin[tag] = LinearNDInterpolator(P, Vals); self.near[tag] = NearestNDInterpolator(P, Vals)
            self.s_lo, self.s_hi = float(s.min()), float(s.max())
            # Australian increment at the two ends (track point of the end latitudes) for use outside the span
            g = d.assign(s=s)
            self.end_inc = getattr(self, 'end_inc', {})
            for end, al in (('south', g.arc_lat.min()), ('north', g.arc_lat.max())):
                tr = g[(g.arc_lat == al) & (g.position == 'track')].iloc[0]
                self.end_inc[(tag, end)] = {o: float(tr[f'v_{o}'] - tr['v_off']) for o in OPTS}

    def lnL(self, lat, lon):
        """dict (option, model tag) -> ln L per point (NaN = not computed)."""
        lat = np.asarray(lat, float); lon = np.asarray(lon, float); n = len(lat)
        s, r = arc_sr(lat, lon); out = {}
        inside = (s >= self.s_lo) & (s <= self.s_hi)
        P = np.column_stack([s[inside], r[inside]])
        for mod, tag in MODELS:
            vi = self.lin[tag](P); bad = ~np.isfinite(vi[:, 0])
            if bad.any():
                vi[bad] = self.near[tag](P[bad])
            ins, nid, W = V.drift_corners(lat, lon)
            ra_off = np.log(V.drift_lookup(ins, nid, W, np.exp(self.N[f'{mod}_h50'] - LREF))) + LREF + self.offset[tag]
            ra_100 = np.log(V.drift_lookup(ins, nid, W, np.exp(self.N[f'{mod}_h100'] - LREF))) + LREF + self.offset[tag]
            south = s < self.s_lo
            for k, o in enumerate(OPTS):
                v = np.full(n, np.nan); v[inside] = vi[:, k]
                if o == 'off':
                    v[~inside] = ra_off[~inside]
                elif o == 'h100':
                    v[~inside] = ra_100[~inside]
                else:
                    inc = np.where(south, self.end_inc[(tag, 'south')][o], self.end_inc[(tag, 'north')][o])
                    v[~inside] = (ra_off + inc)[~inside]
                out[(o, tag)] = v
        out['inside_dedicated_span'] = inside
        return out


class Pleiades:
    def __init__(self):
        m = {}
        for line in (X / 'pleiades/run-j/surfaces/joint-surface-rho0.25-gcrel.toml').read_text().splitlines():
            k, v = line.split(' = ', 1); m[k] = v
        self.nl, self.nn = int(m['nlat']), int(m['nlon']); self.lat0, self.lon0, self.st = float(m['lat0']), float(m['lon0']), float(m['step_deg'])
        self.J = np.fromfile(X / 'pleiades/run-j/surfaces/joint-surface-rho0.25-gcrel.f32', '<f4').reshape(2, self.nl, self.nn).astype(float)
        self.PREF = float(np.nanmax(np.where(np.isfinite(self.J), self.J, np.nan)))

    def cell(self, lat, lon):
        pi = np.floor((lat - (self.lat0 - self.st / 2)) / self.st).astype(np.int64); pj = np.floor((lon - (self.lon0 - self.st / 2)) / self.st).astype(np.int64)
        ok = (pi >= 0) & (pi < self.nl) & (pj >= 0) & (pj < self.nn)
        return pi, pj, ok

    def lnJ(self, lat, lon):
        pi, pj, ok = self.cell(lat, lon); out = {}
        for mi, tag in ((0, 'G'), (1, 'C')):
            v = np.full(len(lat), np.nan); v[ok] = self.J[mi, pi[ok], pj[ok]]; out[tag] = v
        return out
