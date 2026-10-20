#!/usr/bin/env python3
"""Build alternative weather grids for the weather-model sensitivity runs.

Usage: extract.py {merra2|fnl} RAW_DIR OUTPUT.bin [FNL_STAMP ...]

FNL_STAMP (YYYYMMDD_HH, fnl only) selects other analysis times; the default is the MH370
set (7 March 12 UTC to 8 March 06 UTC). The MH371 control uses 20140307_00 _06 _12.

Sources (7-8 March 2014, temperature and u/v wind on pressure levels):
- merra2: NASA MERRA-2 reanalysis inst3_3d_asm_Np (M2I3NPASM v5.12.4), 3-hourly,
  0.5 deg x 0.625 deg, from NASA GES DISC. Needs a NASA Earthdata login in ~/.netrc
  and the "NASA GESDISC DATA ARCHIVE" application approved on the account.
- fnl: NCEP FNL operational global analysis (NCAR GDEX d083002), 6-hourly, 1 deg.
  The closest public analogue of ACCESS-G: an operational analysis, not a reanalysis.
  No login needed.

Output: the binary layout of the ERA5 grid (see crates/flight/src/environment.rs) on
the source's native horizontal grid, longitude -180..180 with the +180 column
duplicating -180. Fields are interpolated linearly in ln(pressure) to the ISA pressure
of each pressure altitude, as for ERA5. Only 20,000-43,000 ft is written: it covers the
model's 25,000-43,000 ft range and avoids below-ground fill values over high terrain.
"""

import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ALTITUDES_FT = [20000.0, 25000.0, 28000.0, 31000.0, 34000.0, 37000.0, 40000.0, 43000.0]


def isa_pressure_hpa(altitude_ft):
    """ICAO standard atmosphere pressure through the lower stratosphere."""
    g, r, lapse, t0, p0 = 9.80665, 287.05287, 0.0065, 288.15, 101325.0
    h = altitude_ft * 0.3048
    p11 = p0 * (1 - lapse * 11000 / t0) ** (g / (r * lapse))
    p = p0 * (1 - lapse * h / t0) ** (g / (r * lapse)) if h <= 11000 else p11 * np.exp(-g * (h - 11000) / (r * 216.65))
    return p / 100.0


def fetch(url, target, netrc=False):
    if target.exists() and target.stat().st_size > 1_000_000:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-sS", "-L", "-f", "-o", target, url]
    if netrc:
        cookies = target.parent / "earthdata.cookies"
        cmd[1:1] = ["-n", "-c", cookies, "-b", cookies]
    subprocess.run(cmd, check=True)


def read_merra2(raw):
    """Returns unix times, pressure levels (hPa, descending), lat, lon (-180..180), {var: [t, lev, lat, lon]}."""
    import h5py

    url = "https://goldsmr5.gesdisc.eosdis.nasa.gov/data/MERRA2/M2I3NPASM.5.12.4/2014/03/"
    wanted = [datetime(2014, 3, 7, h, tzinfo=timezone.utc) for h in (15, 18, 21)] + [
        datetime(2014, 3, 8, h, tzinfo=timezone.utc) for h in (0, 3)
    ]
    times, fields = [], {"T": [], "U": [], "V": []}
    for day in ("20140307", "20140308"):
        path = raw / f"MERRA2_400.inst3_3d_asm_Np.{day}.nc4"
        fetch(url + path.name, path, netrc=True)
        if path.read_bytes()[:4] != b"\x89HDF":
            sys.exit(f"{path.name}: not HDF5 (check the Earthdata account's GES DISC authorisation)")
        with h5py.File(path, "r") as f:
            lev, lat, lon = (f[k][:].astype(float) for k in ("lev", "lat", "lon"))
            start = datetime.strptime(day, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp()
            for k, minutes in enumerate(f["time"][:]):
                t = start + 60 * float(minutes)
                if any(abs(t - w.timestamp()) < 1 for w in wanted):
                    times.append(int(t))
                    for var in fields:
                        fields[var].append(f[var][k].astype(float))
    return times, lev, lat, lon, {"T": fields["T"], "U": fields["U"], "V": fields["V"]}


def read_fnl(raw, stamps=("20140307_12", "20140307_18", "20140308_00", "20140308_06")):
    import pygrib

    times, fields = [], {"T": [], "U": [], "V": []}
    for stamp in stamps:
        path = raw / f"fnl_{stamp}_00.grib2"
        fetch(f"https://data.gdex.ucar.edu/d083002/grib2/2014/2014.03/{path.name}", path)
        g = pygrib.open(str(path))
        levels = None
        for var, short in (("T", "t"), ("U", "u"), ("V", "v")):
            msgs = sorted(g.select(shortName=short, typeOfLevel="isobaricInhPa"), key=lambda m: -m.level)
            levels = np.array([m.level for m in msgs], float)  # descending pressure
            fields[var].append(np.stack([m.values for m in msgs]))
        lats, lons = msgs[0].latlons()
        times.append(int(msgs[0].validDate.replace(tzinfo=timezone.utc).timestamp()))
        g.close()
    lat, lon = lats[:, 0].astype(float), lons[0].astype(float)
    order = np.argsort(np.where(lon >= 180, lon - 360, lon))  # 0..359 -> -180..179
    lon = np.where(lon >= 180, lon - 360, lon)[order]
    for var in fields:
        fields[var] = [a[..., order] for a in fields[var]]
    return times, levels, lat, lon, fields


def to_altitudes(column, lev, targets):
    """column [lev, lat, lon] on descending pressure levels -> [alt, lat, lon]."""
    out = np.empty((len(targets),) + column.shape[1:])
    for i, p in enumerate(targets):
        hi = np.searchsorted(-lev, -p)  # first level at or above p (lower pressure)
        lo = hi - 1
        w = (np.log(p) - np.log(lev[lo])) / (np.log(lev[hi]) - np.log(lev[lo]))
        out[i] = (1 - w) * column[lo] + w * column[hi]
    return out


def main():
    source, raw, output = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    if source == "fnl" and len(sys.argv) > 4:
        times, lev, lat, lon, fields = read_fnl(raw, sys.argv[4:])
    else:
        times, lev, lat, lon, fields = {"merra2": read_merra2, "fnl": read_fnl}[source](raw)
    targets = np.array([isa_pressure_hpa(a) for a in ALTITUDES_FT])
    grids = {}
    for var, columns in fields.items():
        a = np.stack([to_altitudes(c, lev, targets) for c in columns])
        if not np.all(np.isfinite(a)) or np.abs(a).max() > 1e10:
            sys.exit(f"{source} {var}: missing or fill values within 20,000-43,000 ft")
        grids[var] = np.concatenate([a, a[..., :1]], axis=-1)  # +180 column duplicates -180
    lon_out = np.append(lon, 180.0)
    with open(output, "wb") as f:
        f.write(b"MHERA5V1")
        f.write(struct.pack("<4I", len(times), len(ALTITUDES_FT), len(lat), len(lon_out)))
        f.write(np.asarray(times, "<i8").tobytes())
        for axis in (ALTITUDES_FT, lat, lon_out):
            f.write(np.asarray(axis, "<f4").tobytes())
        for var in ("T", "U", "V"):
            f.write(np.ascontiguousarray(grids[var], "<f4").tobytes())
    print(f"{output}: {source}, {len(times)} times x {len(ALTITUDES_FT)} altitudes x {len(lat)} x {len(lon_out)}")


if __name__ == "__main__":
    main()
