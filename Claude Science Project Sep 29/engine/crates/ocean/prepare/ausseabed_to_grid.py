"""Copy the AusSeabed MH370 Phase 1 150 m bathymetry (Geoscience Australia, ga/100315, CC BY 4.0)
unchanged into the crate's raw grid layout, for `bathy::Bathymetry` as its first layer.

The distributed file is a cloud-optimised GeoTIFF on EPSG:3857 (WGS 84 / Pseudo-Mercator), 150 m
projected cells, float32, elevation positive up relative to MSL. No resampling: the layer keeps the
Mercator grid and `bathy.rs` converts lon/lat to Mercator for the nearest-cell lookup. Rows are
written south to north, little-endian float32, nodata -> NaN.

python ausseabed_to_grid.py <cog.tif> <out_dir> <source_zip_sha256>
"""
import hashlib, json, math, os, sys
import numpy as np
import rasterio
from rasterio.windows import Window

tif, out_dir, zip_sha = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)
d = rasterio.open(tif)
assert d.crs.to_epsg() == 3857 and d.count == 1 and d.dtypes[0] == "float32", (d.crs, d.count, d.dtypes)
t = d.transform
assert t.b == 0 and t.d == 0 and t.a == -t.e, t
step = t.a
W, H = d.width, d.height
nodata = d.nodata
out = os.path.join(out_dir, "ausseabed_mh370_150m_elevation.f32")
valid, zmin, zmax, block = 0, math.inf, -math.inf, 512
with open(out, "wb") as f:
    # South to north: file row 0 is the northernmost; write from the bottom block upward.
    for top in range(((H - 1) // block) * block, -1, -block):
        h = min(block, H - top)
        a = d.read(1, window=Window(0, top, W, h)).astype(np.float32)
        bad = ~np.isfinite(a) | (a <= -1e30) | (a == nodata)
        a[bad] = np.nan
        ok = ~bad
        valid += int(ok.sum())
        if ok.any():
            zmin, zmax = min(zmin, float(a[ok].min())), max(zmax, float(a[ok].max()))
        f.write(a[::-1].astype("<f4").tobytes())
sha = hashlib.sha256()
with open(tif, "rb") as g:
    for chunk in iter(lambda: g.read(1 << 24), b""):
        sha.update(chunk)
R = 6378137.0
x0, y0 = t.c + 0.5 * step, t.f - (H - 0.5) * step
manifest = {
    "source": "ausseabed",
    "projection": "epsg3857",
    "x0_m": x0, "y0_m": y0, "step_m": step, "nlon": W, "nlat": H,
    "elevation_file": os.path.basename(out), "elevation_dtype": "f32", "tid_file": None,
    "description": "AusSeabed / Geoscience Australia MH370 Phase 1 150 m bathymetry (GA-4421, GA-4422, GA-4430), "
                   "EPSG:3857 150 m cells copied unchanged (rows south to north), elevation positive up, MSL; nodata NaN",
    "pid": "https://pid.geoscience.gov.au/dataset/ga/100315",
    "licence": "CC BY 4.0",
    "lon_range_deg": [math.degrees(t.c / R), math.degrees((t.c + W * step) / R)],
    "lat_range_deg": [math.degrees(2 * math.atan(math.exp((t.f - H * step) / R)) - math.pi / 2),
                      math.degrees(2 * math.atan(math.exp(t.f / R)) - math.pi / 2)],
    "valid_cells": valid, "elevation_min_m": zmin, "elevation_max_m": zmax,
    "source_sha256": {"mh370_phase1_150m.zip": zip_sha, os.path.basename(tif): sha.hexdigest()},
}
with open(os.path.join(out_dir, "ausseabed_mh370_150m.json"), "w") as g:
    json.dump(manifest, g, indent=1)
print(json.dumps({k: manifest[k] for k in ["nlon", "nlat", "valid_cells", "elevation_min_m", "elevation_max_m", "lon_range_deg", "lat_range_deg"]}))
