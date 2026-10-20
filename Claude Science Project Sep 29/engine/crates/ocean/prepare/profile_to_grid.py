"""Convert GLORYS12V1 full-depth daily fields (uo, vo, thetao, so) and the static `deptho` into the
layout `gridprofile::GridProfile` reads: little-endian f32 (time, lat, lon, variable, depth), NaN at
land and below the floor; `deptho` f32 (lat, lon), NaN on land; and a JSON manifest.

Time placement: the daily means are labelled 00:00 UTC of the averaged day; values are placed at
label + 12 h (the interval centre), as for the surface series (PROVISIONAL until the producer
confirms the label convention; see results/ocean-references.md, GLORYS12V1).

python profile_to_grid.py <fields.nc> <static_bathy.nc> <out_dir>
"""
import json, os, sys
from datetime import datetime, timezone
import h5py
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netcdf_to_grid import attr, decoded, sha256, UNITS

src, static, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
f, s = h5py.File(src, "r"), h5py.File(static, "r")
lon, lat, dep = (f[k][:].astype(np.float64) for k in ("longitude", "latitude", "depth"))
for k, v in (("longitude", lon), ("latitude", lat), ("depth", dep)):
    assert np.allclose(s[k][:], v), k
assert np.all(np.diff(lon) > 0) and np.all(np.diff(lat) > 0) and np.all(np.diff(dep) > 0)
t = f["time"]
unit, _, epoch = attr(t, "units").partition(" since ")
e = datetime.fromisoformat(epoch.strip().replace(" ", "T")).replace(tzinfo=timezone.utc).timestamp()
labels = e + t[:].astype(np.float64) * UNITS[unit.strip()]
times = labels + 12 * 3600.0
names = ["uo", "vo", "thetao", "so"]
nt, nz, ny, nx = f["uo"].shape
stem = os.path.splitext(os.path.basename(src))[0]
data = os.path.join(out, stem + ".profile.f32")
with open(data, "wb") as g:
    for it in range(nt):
        block = np.stack([decoded(f[n], (it,)) for n in names])      # (var, z, y, x)
        g.write(np.ascontiguousarray(block.transpose(2, 3, 0, 1)).astype("<f4").tobytes())  # (y, x, var, z)
d = decoded(s["deptho"], ())
dfile = os.path.join(out, "glorys12v1_deptho.f32")
d.astype("<f4").tofile(dfile)
m = {
    "product": "glorys12v1",
    "description": f"GLORYS12V1 daily means uo, vo, thetao, so, all {nz} levels, from {os.path.basename(src)}; "
                   "placed at label + 12 h (PROVISIONAL); deptho from the static dataset",
    "lon": lon.tolist(), "lat": lat.tolist(), "depth_m": dep.tolist(), "time_unix_s": times.tolist(),
    "time_labels_unix_s": labels.tolist(), "variables": names,
    "data_file": os.path.basename(data), "deptho_file": os.path.basename(dfile),
    "source_sha256": {os.path.basename(src): sha256(src), os.path.basename(static): sha256(static)},
    "derived_sha256": {os.path.basename(data): sha256(data), os.path.basename(dfile): sha256(dfile)},
}
with open(os.path.join(out, stem + ".profile.json"), "w") as g:
    json.dump(m, g)
print(json.dumps({"shape": [nt, nz, ny, nx], "first_time": datetime.fromtimestamp(times[0], timezone.utc).isoformat(),
                  "bytes": os.path.getsize(data), "deptho_range": [float(np.nanmin(d)), float(np.nanmax(d))],
                  "derived_sha256": m["derived_sha256"]}))
