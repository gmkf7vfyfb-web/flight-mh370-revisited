"""Settling transform for the Kadri / Haixun conditional test (pre-registration Q8).

A vectorised Python port of hypotheses/settling/physics.rs (hypothesis/settling 9330d4c): terminal-speed
descent layer by layer (dz = 50 m), current from a gridded column (hold deepest level below the model
bottom), glide as a heading random walk (diffusive limit when memory <= dz), banded uniform-offset ocean
error realised once per draw (0.10 m/s x [1.0, 0.5, 0.2, 0.3] for surface <100 m / upper <1000 m / deep /
within 200 m of seabed), carry along the impact track, float phase (surface current + leeway x 10 m wind +
diffusion) for elements that do not sink at once, seabed = AusSeabed 150 m first, GEBCO_2026 elsewhere;
calculation stops at first seabed contact.
Element classes are breakup.toml (same commit) plus one NEW class declared here: the detached flight
recorder (SSFDR/SSCVR, educated estimate). 'Recorder retained in the aft fuselage' uses the family's
fuselage-section class.
"""
import numpy as np, json, os
OD = os.path.expanduser('~/Downloads/mh370-ocean-data')
RE = 6371000.0

# ----------------------------------------------------------------------------------- bathymetry
_aj = json.load(open(f'{OD}/ausseabed/grid/ausseabed_mh370_150m.json'))
_gj = json.load(open(f'{OD}/gebco/grid/gebco_2026.json'))
_A = np.memmap(f'{OD}/ausseabed/grid/{_aj["elevation_file"]}', dtype='<f4', mode='r', shape=(_aj['nlat'], _aj['nlon']))
_G = np.memmap(f'{OD}/gebco/grid/{_gj["elevation_file"]}', dtype='<i2', mode='r', shape=(_gj['nlat'], _gj['nlon']))
_T = np.memmap(f'{OD}/gebco/grid/{_gj["tid_file"]}', dtype='u1', mode='r', shape=(_gj['nlat'], _gj['nlon']))
RM = 6378137.0

def seabed(lat, lon, with_src=False):
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    x = RM * np.radians(lon); y = RM * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
    i = np.rint((y - _aj['y0_m']) / _aj['step_m']).astype(np.int64); j = np.rint((x - _aj['x0_m']) / _aj['step_m']).astype(np.int64)
    ok = (i >= 0) & (i < _aj['nlat']) & (j >= 0) & (j < _aj['nlon'])
    a = np.full(lat.shape, np.nan); a[ok] = _A[i[ok], j[ok]]
    gi = np.rint((lat - _gj['lat0']) / _gj['step_deg']).astype(np.int64); gj = np.rint((lon - _gj['lon0']) / _gj['step_deg']).astype(np.int64)
    g = _G[gi, gj].astype(float)
    d = np.where(np.isfinite(a), -a, -g)
    if with_src:
        return d, np.isfinite(a), _T[gi, gj]
    return d

# ----------------------------------------------------------------------------------- ocean
class Ocean:
    """Gridded column: U, V [t, lat, lon, z] (NaN below bottom filled by hold-deepest-level), rho(z) profile."""
    def __init__(self, label, lat, lon, tt, z, U, V, rho_z, rho_vals, model_bottom):
        self.label, self.lat, self.lon, self.tt, self.z = label, lat, lon, tt, z
        self.U, self.V, self.rho_z, self.rho_vals, self.model_bottom = U, V, rho_z, rho_vals, model_bottom

    def _w(self, grid, x):
        f = np.interp(x, grid, np.arange(len(grid)))
        i0 = np.clip(np.floor(f).astype(int), 0, len(grid) - 2); return i0, np.clip(f - i0, 0, 1)

    def uv(self, lat, lon, t, z):
        i, wi = self._w(self.lat, lat); j, wj = self._w(self.lon, lon); k, wt = self._w(self.tt, t)
        if np.isscalar(z) or np.ndim(z) == 0:
            z = np.full(lat.shape, float(z))
        l, wl = self._w(self.z, z)
        u = np.zeros(lat.shape); v = np.zeros(lat.shape)
        for a, fa in ((0, 1 - wt), (1, wt)):
            for b, fb in ((0, 1 - wi), (1, wi)):
                for c, fc in ((0, 1 - wj), (1, wj)):
                    for d, fd in ((0, 1 - wl), (1, wl)):
                        f = fa * fb * fc * fd
                        u += f * self.U[k + a, i + b, j + c, l + d]; v += f * self.V[k + a, i + b, j + c, l + d]
        return u, v

    def rho(self, z):
        return np.interp(z, self.rho_z, self.rho_vals)

def hold_deepest(X):
    """Forward-fill NaN along the last (depth) axis with the deepest valid value; count valid levels."""
    X = X.copy(); valid = np.isfinite(X)
    nvalid = valid.sum(-1)
    for k in range(1, X.shape[-1]):
        m = ~np.isfinite(X[..., k]); X[..., k][m] = X[..., k - 1][m]
    return np.nan_to_num(X), nvalid

class Wind:
    def __init__(self, box=(-32.0, -19.0, 94.0, 108.0)):
        ej = json.load(open(f'{OD}/era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json'))
        lat = np.array(ej['lat']); lon = np.array(ej['lon']); tt = np.array(ej['time_unix_s'])
        M = np.memmap(f'{OD}/era5/{ej["data_file"]}', dtype='<f4', mode='r', shape=(len(tt), len(lat), len(lon), 2))
        it = np.where(tt <= 1394150400 + 4 * 86400)[0]
        ia = np.where((lat >= box[0]) & (lat <= box[1]))[0]; io = np.where((lon >= box[2]) & (lon <= box[3]))[0]
        self.W = np.asarray(M[it[0]:it[-1] + 1, ia[0]:ia[-1] + 1, io[0]:io[-1] + 1])
        self.lat, self.lon, self.tt = lat[ia], lon[io], tt[it]

    def uv(self, lat, lon, t):
        def w(grid, x):
            f = np.interp(x, grid, np.arange(len(grid))); i0 = np.clip(np.floor(f).astype(int), 0, len(grid) - 2); return i0, np.clip(f - i0, 0, 1)
        i, wi = w(self.lat, lat); j, wj = w(self.lon, lon); k, wt = w(self.tt, t)
        out = np.zeros(lat.shape + (2,))
        for a, fa in ((0, 1 - wt), (1, wt)):
            for b, fb in ((0, 1 - wi), (1, wi)):
                for c, fc in ((0, 1 - wj), (1, wj)):
                    out += (fa * fb * fc)[:, None] * self.W[k + a, i + b, j + c]
        return out[:, 0], out[:, 1]

# ----------------------------------------------------------------------------------- elements
def U(lo, hi): return ('u', lo, hi)
def LU(lo, hi): return ('l', lo, hi)
def C(x): return ('u', x, x)

BASE = {
 'engine': dict(s=LU(400, 1300), rm=U(3500, 6000), cd=U(0.8, 1.2), df=C(1.0), g=U(0, 0.2), gl=LU(20, 200), carry=U(0, 1), lat_=0.3, sao=1.0, fl=C(0), lw=C(0)),
 'landing-gear': dict(s=LU(350, 1200), rm=U(2500, 5500), cd=U(0.9, 1.3), df=C(1.0), g=U(0, 0.2), gl=LU(20, 200), carry=U(0, 1), lat_=0.3, sao=1.0, fl=C(0), lw=C(0)),
 'fuselage-section': dict(s=LU(60, 250), rm=U(2000, 2800), cd=U(0.8, 1.2), df=U(1.0, 1.3), g=U(0, 0.4), gl=LU(20, 300), carry=U(0, 1), lat_=0.3, sao=0.7, fl=LU(60, 3600), lw=U(0.01, 0.04)),
 # NEW (declared educated estimate, not in breakup.toml): detached SSFDR / SSCVR (1/2 ATR short chassis about
 # 0.124 x 0.194 x 0.318 m, 4-8 kg, or the crash-survivable memory unit alone), flooded chassis + steel/titanium
 # armour. Areal density from the smallest to the largest face; tumbles (descent factor up to 1.3), short glide memory.
 'recorder-detached': dict(s=LU(65, 330), rm=U(2700, 5000), cd=U(0.8, 1.2), df=U(1.0, 1.3), g=U(0, 0.3), gl=LU(1, 20), carry=U(0, 1), lat_=0.3, sao=1.0, fl=C(0), lw=C(0)),
}
FAMILY = {  # breakup.toml family overrides for the classes used here; families 0 intact, 1 broken, 2 fragmented
 0: {'engine': dict(carry=U(0, 3)), 'landing-gear': dict(carry=U(0, 3)), 'recorder-detached': dict(carry=U(0, 3)),
     'fuselage-section': dict(s=LU(150, 350), rm=U(1800, 2700), g=U(0, 0.3), gl=LU(100, 2000), carry=U(1, 4), sao=0.0, fl=LU(600, 21600))},
 1: {},
 2: {'fuselage-section': dict(s=LU(30, 150), g=U(0.1, 0.6), gl=LU(5, 100), sao=0.9, fl=LU(60, 1800))},
}

def draw(spec, u):
    kind, lo, hi = spec
    return np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo))) if kind == 'l' else lo + u * (hi - lo)

def params(cls, fam, rng):
    n = len(fam); out = {}
    keys = ['s', 'rm', 'cd', 'df', 'g', 'gl', 'carry', 'fl', 'lw']
    for k in keys: out[k] = np.empty(n)
    out['lat_'] = np.empty(n); out['sao'] = np.empty(n)
    for f in (0, 1, 2):
        m = fam == f
        if not m.any(): continue
        p = dict(BASE[cls]); p.update(FAMILY[f].get(cls, {}))
        for k in keys: out[k][m] = draw(p[k], rng.uniform(size=m.sum()))
        out['lat_'][m] = p['lat_']; out['sao'][m] = p['sao']
    return out

# ----------------------------------------------------------------------------------- integration
def move(lat, lon, dx, dy):
    lat2 = lat + np.degrees(dy / RE); lon2 = lon + np.degrees(dx / (RE * np.cos(np.radians(0.5 * (lat + lat2)))))
    return lat2, lon2

def settle(lat0, lon0, t0, vh, track_deg, fam, cls, ocean, wind, rng, terms=('carry', 'float', 'current', 'glide', 'ocean-error', 'diffusion'),
           sigma_err=0.10, factors=(1.0, 0.5, 0.2, 0.3), K_range=(10.0, 200.0), step_m=50.0, float_step_s=600.0):
    n = len(lat0); p = params(cls, fam, rng)
    lat = np.array(lat0, float); lon = np.array(lon0, float); t = np.array(t0, float)
    # ocean error: one realisation per draw, independent per band (surface, upper, deep, near-bottom)
    err = rng.normal(size=(n, 4, 2)) * sigma_err * np.array(factors)[None, :, None]
    if 'ocean-error' not in terms: err[:] = 0
    # carry along the impact track
    along = vh * p['carry'] if 'carry' in terms else np.zeros(n)
    cross = rng.normal(size=n) * p['lat_'] * along
    tr = np.radians(track_deg)
    dx = along * np.sin(tr) + cross * np.cos(tr); dy = along * np.cos(tr) - cross * np.sin(tr)
    lat, lon = move(lat, lon, dx, dy)
    # float phase
    floats = (rng.uniform(size=n) >= p['sao']) & ('float' in terms)
    tf = np.where(floats, p['fl'], 0.0)
    K = np.exp(np.log(K_range[0]) + rng.uniform(size=n) * np.log(K_range[1] / K_range[0])) if 'diffusion' in terms else np.zeros(n)
    el = np.zeros(n)
    while True:
        act = el < tf
        if not act.any(): break
        dt = np.minimum(float_step_s, tf - el)[act]
        la, lo, tt = lat[act], lon[act], t[act] + 0.5 * dt
        u, v = ocean.uv(la, lo, tt, ocean.z[0]) if 'current' in terms else (np.zeros(act.sum()), np.zeros(act.sum()))
        wu, wv = wind.uv(la, lo, tt)
        lw = p['lw'][act]
        ux = u + lw * wu + err[act, 0, 0]; vy = v + lw * wv + err[act, 0, 1]
        sd = np.sqrt(2 * K[act] * dt)
        ddx = ux * dt + sd * rng.normal(size=act.sum()); ddy = vy * dt + sd * rng.normal(size=act.sum())
        lat[act], lon[act] = move(la, lo, ddx, ddy); t[act] += dt; el[act] += dt
    release_lat, release_lon = lat.copy(), lon.copy()
    # descent
    z = np.zeros(n); done = np.zeros(n, bool); below = np.zeros(n); desc = np.zeros(n)
    floor = seabed(lat, lon)
    heading = rng.uniform(0, 2 * np.pi, size=n)
    g = p['g'] if 'glide' in terms else np.zeros(n); l = p['gl']
    out_lat = np.full(n, np.nan); out_lon = np.full(n, np.nan); out_z = np.full(n, np.nan)
    for _ in range(400):
        a = ~done
        if not a.any(): break
        mid = z[a] + step_m / 2
        rho = ocean.rho(mid)
        bu = 1 - rho / p['rm'][a]
        w = p['df'][a] * np.sqrt(2 * 9.80665 * p['s'][a] * bu / (rho * p['cd'][a]))
        dt = step_m / w
        if 'current' in terms:
            u, v = ocean.uv(lat[a], lon[a], t[a] + dt / 2, mid)
        else:
            u = np.zeros(a.sum()); v = np.zeros(a.sum())
        fl_a = floor[a]
        band = np.where(fl_a - mid <= 200.0, 3, np.where(mid < 100, 0, np.where(mid < 1000, 1, 2)))
        e = err[a][np.arange(a.sum()), band]
        sx = (u + e[:, 0]) * dt; sy = (v + e[:, 1]) * dt
        la_, ga_ = l[a], g[a]
        diff = la_ <= step_m
        sd = ga_ * np.sqrt(la_ * step_m)
        nx = rng.normal(size=a.sum()); ny = rng.normal(size=a.sum())
        sx = sx + np.where(diff, sd * nx, 0); sy = sy + np.where(diff, sd * ny, 0)
        hd = heading[a]
        nsub = np.where(diff, 0, np.ceil(10 * step_m / la_)).astype(int)
        for s_ in range(int(nsub.max()) if nsub.size else 0):
            m = nsub > s_
            h = step_m / np.maximum(nsub, 1)
            sx = sx + np.where(m, ga_ * h * np.sin(hd), 0); sy = sy + np.where(m, ga_ * h * np.cos(hd), 0)
            hd = hd + np.where(m, np.sqrt(2 * h / la_) * rng.normal(size=a.sum()), 0)
        heading[a] = hd
        nla, nlo = move(lat[a], lon[a], sx, sy)
        nfl = seabed(nla, nlo)
        zz = z[a]
        hit = zz + step_m >= nfl
        beyond = mid > ocean.model_bottom(lat[a], lon[a])
        denom = step_m - (nfl - fl_a)
        f = np.where(denom > 0, np.clip((fl_a - zz) / np.where(denom > 0, denom, 1), 0, 1), 0.0)
        idx = np.where(a)[0]
        hi = idx[hit]
        out_lat[hi] = lat[hi] + (nla[hit] - lat[hi]) * f[hit]; out_lon[hi] = lon[hi] + (nlo[hit] - lon[hi]) * f[hit]
        out_z[hi] = zz[hit] + f[hit] * step_m; desc[hi] += f[hit] * dt[hit]; below[hi] += np.where(beyond[hit], f[hit] * step_m, 0)
        done[hi] = True
        mi = idx[~hit]
        lat[mi] = nla[~hit]; lon[mi] = nlo[~hit]; floor[mi] = nfl[~hit]; z[mi] += step_m; t[mi] += dt[~hit]; desc[mi] += dt[~hit]
        below[mi] += np.where(beyond[~hit], step_m, 0)
    return dict(lat=out_lat, lon=out_lon, depth=out_z, descent_s=desc, float_s=tf, floated=floats, below_m=below,
                release_lat=release_lat, release_lon=release_lon)

def offsets_km(lat0, lon0, lat1, lon1):
    dy = np.radians(lat1 - lat0) * RE / 1e3; dx = np.radians(lon1 - lon0) * RE * np.cos(np.radians(0.5 * (lat0 + lat1))) / 1e3
    return dx, dy
