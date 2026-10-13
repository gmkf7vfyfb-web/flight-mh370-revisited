"""Independent re-implementation used by results/drift-model-audit-architecture.md (test 2).
Reads the producers' netCDF files directly (not the converted .f32 grids), CF-decodes them, places daily
means at label + 12 h, interpolates trilinearly with land renormalisation (the shared crate's stated
semantics, coded independently) and advects with RK2 midpoint (6 h) or RK4 (1 h) on the sphere.
Usage: see run_crossimpl() at the bottom; requires h5py, numpy."""
import numpy as np, h5py
from datetime import datetime, timezone
RE = 6371008.8

class NCField:
    def __init__(self, files, uvar, vvar, t_lo, t_hi, shift_h):
        T, U, V = [], [], []
        for fn in files:
            with h5py.File(fn, "r") as f:
                tu = f["time"].attrs["units"]; tu = tu.decode() if isinstance(tu, bytes) else tu
                step, _, orig = tu.split(" ", 2); orig = orig.replace("T", " ").split("+")[0].strip()
                o = datetime.fromisoformat(orig).replace(tzinfo=timezone.utc).timestamp()
                t = o + f["time"][:].astype(np.float64) * {"hours": 3600., "days": 86400., "seconds": 1.}[step] + shift_h * 3600.
                sel = np.where((t >= t_lo) & (t <= t_hi))[0]
                if len(sel) == 0: continue
                lat = f["latitude"][:].astype(np.float64); lon = f["longitude"][:].astype(np.float64)
                def dec(name):
                    v = f[name]; raw = v[sel[0]:sel[-1] + 1]
                    if raw.ndim == 4: raw = raw[:, 0]
                    out = raw.astype(np.float64) * float(np.ravel(v.attrs.get("scale_factor", 1.0))[0]) + float(np.ravel(v.attrs.get("add_offset", 0.0))[0])
                    fill = v.attrs.get("_FillValue")
                    if fill is not None: out[raw == np.ravel(fill)[0]] = np.nan
                    return out
                u, v = dec(uvar), dec(vvar)
                if lat[0] > lat[-1]: lat, u, v = lat[::-1], u[:, ::-1], v[:, ::-1]
                T.append(t[sel]); U.append(u); V.append(v)
        self.t, self.u, self.v, self.lat, self.lon = np.concatenate(T), np.concatenate(U), np.concatenate(V), lat, lon
        assert np.all(np.diff(self.t) > 0)
    def sample(self, t, lon, lat):
        def br(ax, x):
            i = np.clip(np.searchsorted(ax, x, side="right") - 1, 0, len(ax) - 2)
            return i, (x - ax[i]) / (ax[i + 1] - ax[i]), (x >= ax[0]) & (x <= ax[-1])
        it, wt, o1 = br(self.t, np.full_like(lon, t)); iy, wy, o2 = br(self.lat, lat); ix, wx, o3 = br(self.lon, lon)
        au = np.zeros_like(lon); av = np.zeros_like(lon); tot = np.zeros_like(lon)
        for dt, ft in ((0, 1 - wt), (1, wt)):
            for dy, fy in ((0, 1 - wy), (1, wy)):
                for dx, fx in ((0, 1 - wx), (1, wx)):
                    w = ft * fy * fx; uu = self.u[it + dt, iy + dy, ix + dx]; vv = self.v[it + dt, iy + dy, ix + dx]
                    g = np.isfinite(uu) & np.isfinite(vv) & (w > 0)
                    au += np.where(g, w * np.nan_to_num(uu), 0); av += np.where(g, w * np.nan_to_num(vv), 0); tot += np.where(g, w, 0)
        ok = o1 & o2 & o3 & (tot > 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(ok, au / tot, np.nan), np.where(ok, av / tot, np.nan)

def displace(lon, lat, de, dn):
    lat1 = lat + np.degrees(dn / RE); cm = np.maximum(np.cos(np.radians((lat + lat1) / 2)), 1e-8)
    return lon + np.degrees(de / (RE * cm)), lat1

def advect(field, lon, lat, t0, out_times, dt, scheme="rk2"):
    lon, lat, t, res = np.array(lon, float), np.array(lat, float), t0, []
    for ot in out_times:
        while t < ot - 1e-6:
            h = min(dt, ot - t)
            if scheme == "rk2":
                u1, v1 = field.sample(t, lon, lat); xm, ym = displace(lon, lat, u1 * h / 2, v1 * h / 2)
                u2, v2 = field.sample(t + h / 2, xm, ym); lon, lat = displace(lon, lat, u2 * h, v2 * h)
            else:
                u1, v1 = field.sample(t, lon, lat); x2, y2 = displace(lon, lat, u1 * h / 2, v1 * h / 2)
                u2, v2 = field.sample(t + h / 2, x2, y2); x3, y3 = displace(lon, lat, u2 * h / 2, v2 * h / 2)
                u3, v3 = field.sample(t + h / 2, x3, y3); x4, y4 = displace(lon, lat, u3 * h, v3 * h)
                u4, v4 = field.sample(t + h, x4, y4)
                lon, lat = displace(lon, lat, (u1 + 2 * u2 + 2 * u3 + u4) * h / 6, (v1 + 2 * v2 + 2 * v3 + v4) * h / 6)
            t += h
        res.append((lon.copy(), lat.copy()))
    return res
