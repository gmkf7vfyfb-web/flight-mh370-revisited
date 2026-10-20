"""WOA23 1-degree climatology -> TEOS-10 sound-speed grids with spread, for `SoundSpeedClimatology`.

Mean: the epoch's decade (t_an, s_an). Spread: the objectively analysed standard deviations (t_sdo,
s_sdo) of the all-decade climatology `decav` (1955-2022), for the same month/season. Reason: the
decadal *_sd fields exist only where a cell had observations (16-38% of cells) and the decadal *_sdo
are exactly zero in about 30% of 1995-2004 ocean cells, which would declare a sparsely sampled profile
perfectly known. The all-decade *_sdo describes month-specific variability over every year, which is
the spread of an unobserved year's profile. Zero spreads that remain are counted and reported, not
floored.

For each decade (95A4, A5B4, B5C2) and month 1-12: monthly t_an/s_an/t_sd/s_sd on WOA's levels down to
1,500 m, and the matching season's (Jan-Mar = 13, Apr-Jun = 14, Jul-Sep = 15, Oct-Dec = 16) on the deeper
levels, as WOA distributes them. Then, with official TEOS-10 (`gsw`):
    p  = p_from_z(-z, lat);  SA = SA_from_SP(SP, p, lon, lat);  CT = CT_from_t(SA, t, p)
    c  = sound_speed(SA, CT, p)
    c_sd = sqrt((dc/dt * t_sd)^2 + (dc/dSP * s_sd)^2), derivatives by central differences
           (dt = 0.01 degC, dSP = 0.01), T and S deviations treated as independent (declared).
WOA temperature is in-situ (ITS-90) and salinity practical. No value is filled: a level WOA has no data
for stays NaN. Region 40-180 E, 60 S-30 N (Indian Ocean paths and H11).

    python woa23_to_soundspeed.py <woa23-dir> <out-dir> [lon0 lon1 lat0 lat1 [decade ...]]

The optional region (and decades) build the same files for another area into their own directory, e.g.
the north-west Pacific for the F-35A -> H11 path (130-180 E, 15-50 N, decade B5C2). Without them the
default region and all three decades are written exactly as before.
"""
import json
import os
import sys

import gsw
import h5py
import numpy as np

LON, LAT = (40.0, 180.0), (-60.0, 30.0)
SEASON = {1: 13, 2: 13, 3: 13, 4: 14, 5: 14, 6: 14, 7: 15, 8: 15, 9: 15, 10: 16, 11: 16, 12: 16}


def read(path, names):
    with h5py.File(path, "r") as f:
        lon, lat, depth = f["lon"][:], f["lat"][:], f["depth"][:]
        i = np.where((lon >= LON[0]) & (lon <= LON[1]))[0]
        j = np.where((lat >= LAT[0]) & (lat <= LAT[1]))[0]
        out = {}
        for n in names:
            v = f[n]
            x = v[0, :, j[0]:j[-1] + 1, i[0]:i[-1] + 1].astype(np.float64)
            fill = v.attrs.get("_FillValue")
            if fill is not None:
                x[x == fill[0]] = np.nan
            x[np.abs(x) > 1e30] = np.nan
            out[n] = x
    return lon[i].astype(float), lat[j].astype(float), depth.astype(float), out


def main():
    global LON, LAT
    src, out = sys.argv[1], sys.argv[2]
    decades = ("95A4", "A5B4", "B5C2")
    if len(sys.argv) > 6:
        LON, LAT = (float(sys.argv[3]), float(sys.argv[4])), (float(sys.argv[5]), float(sys.argv[6]))
        decades = tuple(sys.argv[7:]) or decades
    os.makedirs(out, exist_ok=True)
    for dec in decades:
        for month in range(1, 13):
            f = lambda v, tt: os.path.join(src, f"woa23_{dec}_{v}{tt:02d}_01.nc")
            g = lambda v, tt: os.path.join(src, f"woa23_decav_{v}{tt:02d}_01.nc")
            lon, lat, zm, tm = read(f("t", month), ["t_an"])
            _, _, _, sm = read(f("s", month), ["s_an"])
            _, _, zs, ts = read(f("t", SEASON[month]), ["t_an"])
            _, _, _, ss = read(f("s", SEASON[month]), ["s_an"])
            tm["t_sd"] = read(g("t", month), ["t_sdo"])[3]["t_sdo"]
            sm["s_sd"] = read(g("s", month), ["s_sdo"])[3]["s_sdo"]
            ts["t_sd"] = read(g("t", SEASON[month]), ["t_sdo"])[3]["t_sdo"]
            ss["s_sd"] = read(g("s", SEASON[month]), ["s_sdo"])[3]["s_sdo"]
            deep = zs > zm[-1]
            z = np.concatenate([zm, zs[deep]])
            cat = lambda a, b: np.concatenate([a, b[deep]], axis=0)
            t, tsd = cat(tm["t_an"], ts["t_an"]), cat(tm["t_sd"], ts["t_sd"])
            s, ssd = cat(sm["s_an"], ss["s_an"]), cat(sm["s_sd"], ss["s_sd"])
            Z, LA, LO = np.meshgrid(z, lat, lon, indexing="ij")
            p = gsw.p_from_z(-Z, LA)

            def c_of(tt, sp):
                sa = gsw.SA_from_SP(sp, p, LO, LA)
                return gsw.sound_speed(sa, gsw.CT_from_t(sa, tt, p), p), sa

            c, sa = c_of(t, s)
            ct = gsw.CT_from_t(sa, t, p)
            dcdt = (c_of(t + 0.01, s)[0] - c_of(t - 0.01, s)[0]) / 0.02
            dcds = (c_of(t, s + 0.01)[0] - c_of(t, s - 0.01)[0]) / 0.02
            csd = np.sqrt((dcdt * tsd) ** 2 + (dcds * ssd) ** 2)
            stem = f"woa23_{dec}_m{month:02d}"
            files = {}
            for name, arr in (("c_mean", c), ("c_sd", csd), ("sa", sa), ("ct", ct)):
                fn = f"{stem}_{name}.f32"
                np.ascontiguousarray(np.moveaxis(arr, 0, -1)).astype("<f4").tofile(os.path.join(out, fn))  # [lat][lon][level]
                files[name + "_file"] = fn
            manifest = dict(product="woa23", decade=dec, month=month, lon0=float(lon[0]), lat0=float(lat[0]),
                            step_deg=float(lon[1] - lon[0]), nlon=len(lon), nlat=len(lat), depth_m=z.tolist(),
                            monthly_to_m=float(zm[-1]), seasonal_file=SEASON[month],
                            sd_method="linearised; decav t_sdo/s_sdo; T and S deviations independent",
                            zero_sd_fraction=float(np.mean(csd[np.isfinite(c)] == 0)), **files)
            json.dump(manifest, open(os.path.join(out, stem + ".json"), "w"))
            print(json.dumps(dict(stem=stem, levels=len(z), c_range=[float(np.nanmin(c)), float(np.nanmax(c))],
                                  c_sd_median=float(np.nanmedian(csd)),
                                  zero_sd_fraction=round(float(np.mean(csd[np.isfinite(c)] == 0)), 4))), flush=True)


if __name__ == "__main__":
    main()
