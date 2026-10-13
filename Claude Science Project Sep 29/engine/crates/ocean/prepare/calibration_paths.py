"""Acoustic path sections for two Atlantic calibration events (hydroacoustics audit task 2c, pre-registered at
23add102), built with the audit's own builder `results/hydroacoustics-audit/scripts/paths.py` so the files are in
the schema the module's KRAKEN wrapper reads (bathy_<name>.csv, ssp_<name>.csv).

The builder is used UNCHANGED. Only its two data loaders are pointed at South Atlantic layers, built from the same
GEBCO_2026 and WOA23 sources as the Indian Ocean layers with the region options of gebco_to_grid.py and
woa23_to_soundspeed.py (-62..-12 E, -48..6 N). After build(), two columns the builder leaves NaN are filled here:
`tid` (GEBCO Type Identifier of the centre cell) and `corridor_max_elevation_m` (highest elevation within +-2 km
cross-track, sampled every 250 m on the perpendicular geodesics, nearest GEBCO cell, as in the shared crate). A
`<name>_meta.json` records the inputs, and `<name>_shallow.csv` lists every along-track stretch shallower than
1,000 m (track 3x3 median, and corridor maximum).

python calibration_paths.py <repo root> <out_dir>
"""
import hashlib, importlib.util, json, pathlib, sys
import numpy as np, pandas as pd
from pyproj import Geod

repo, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("paths", repo / "Claude Science Project Sep 29/results/hydroacoustics-audit/scripts/paths.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
OCEAN = P.OCEAN
GEB = OCEAN / "gebco/grid/gebco_2026_satl.json"
WOA = OCEAN / "woa23/soundspeed_satl"


def gebco_satl():
    if P._gebco is None:
        m = json.loads(GEB.read_text())
        z = np.memmap(GEB.parent / m["elevation_file"], dtype="<i2", mode="r", shape=(m["nlat"], m["nlon"]))
        P._gebco = (m, z)
    return P._gebco


def woa_satl(decade, month):
    m = json.loads((WOA / f"woa23_{decade}_m{month:02d}.json").read_text())
    shp = (m["nlat"], m["nlon"], len(m["depth_m"]))
    g = {k: np.fromfile(WOA / m[f"{k}_file"], dtype="<f4").reshape(shp) for k in ("c_mean", "sa", "ct")}
    return m, g


P.gebco, P.woa = gebco_satl, woa_satl
m, z = gebco_satl()
tid = np.memmap(GEB.parent / m["tid_file"], dtype="u1", mode="r", shape=(m["nlat"], m["nlon"]))
G = Geod(ellps="WGS84")


def cell(lat, lon):
    return np.rint((lat - m["lat0"]) / m["step_deg"]).astype(int), np.rint((lon - m["lon0"]) / m["step_deg"]).astype(int)


EVENTS = [
    # name, source (lat, lon), receiver (lat, lon), WOA23 decade, month, event date, notes
    ("af447-H10S", (3.07, -30.56), (-8.95, -14.65), "A5B4", 6, "2009-06-01", "AF447 impact (architect's coordinates) to IMS H10S, Ascension"),
    ("sanjuan-charge-H10N", (-45.67, -59.24), (-7.84, -14.49), "B5C2", 12, "2017-12-01", "ARA San Juan calibration charge (architect's coordinates) to IMS H10N, Ascension"),
]
summary = []
for name, a, b, dec, mon, date, note in EVENTS:
    L, shallow_builder = P.build(name, a, b, dec, mon, out)
    f = out / f"bathy_{name}.csv"
    d = pd.read_csv(f)
    i, j = cell(d.lat.values, d.lon.values)
    d["tid"] = tid[i, j].astype(int)
    # corridor maximum, +-2 km at 250 m on the perpendiculars
    az = np.empty(len(d))
    fa, _, _ = G.inv(d.lon.values[:-1], d.lat.values[:-1], d.lon.values[1:], d.lat.values[1:])
    az[:-1] = fa; az[-1] = fa[-1]
    cm = np.full(len(d), -np.inf)
    for off in np.arange(0.0, 2000.0 + 1, 250.0):
        for side in (90.0, -90.0):
            lo, la, _ = G.fwd(d.lon.values, d.lat.values, az + side, np.full(len(d), off))
            ii, jj = cell(la, lo)
            cm = np.maximum(cm, z[ii, jj].astype(float))
    d["corridor_max_elevation_m"] = cm
    d.to_csv(f, index=False)
    # shallow stretches (< 1,000 m water depth)
    rows = []
    for col in ("elevation_m", "corridor_max_elevation_m"):
        sh = (d[col].values > -1000.0)
        k = 0
        while k < len(sh):
            if sh[k]:
                e = k
                while e + 1 < len(sh) and sh[e + 1]:
                    e += 1
                seg = d.iloc[k:e + 1]
                top = seg[col].idxmax()
                rows.append(dict(measure="track_3x3_median" if col == "elevation_m" else "corridor_max_2km", start_km=round(seg.range_km.iloc[0], 1),
                                 end_km=round(seg.range_km.iloc[-1], 1), shallowest_elevation_m=float(d.loc[top, col]),
                                 at_lat=round(d.loc[top, "lat"], 4), at_lon=round(d.loc[top, "lon"], 4), tid=int(d.loc[top, "tid"])))
                k = e + 1
            else:
                k += 1
    pd.DataFrame(rows, columns=["measure", "start_km", "end_km", "shallowest_elevation_m", "at_lat", "at_lon", "tid"]).to_csv(out / f"{name}_shallow.csv", index=False)
    ssp = pd.read_csv(out / f"ssp_{name}.csv")
    meta = dict(name=name, note=note, source_lat_lon=a, receiver_lat_lon=b, event_date=date, geodesic_length_km=round(L, 3),
                spacing_km=0.5, depth="median of the 3x3 GEBCO_2026 cells (paths.py)", woa23=dict(decade=dec, month=mon, interpolation="bilinear, 25 km nodes (paths.py)"),
                gebco_layer=str(GEB), gebco_source_sha256=m["source_sha256"], woa23_dir=str(WOA),
                builder="results/hydroacoustics-audit/scripts/paths.py (unchanged; loaders redirected)",
                filled_here=["tid (centre cell)", "corridor_max_elevation_m (+-2 km, 250 m, nearest cell)"],
                samples=len(d), ssp_nodes=int(ssp.node.nunique()), builder_shallow_excluding_last_100km_m=shallow_builder,
                track_depth_range_m=[float(-d.elevation_m.max()), float(-d.elevation_m.min())])
    (out / f"{name}_meta.json").write_text(json.dumps(meta, indent=1))
    summary.append(dict(meta, shallow_stretches=rows))
print(json.dumps([{k: s[k] for k in ("name", "geodesic_length_km", "samples", "ssp_nodes", "track_depth_range_m", "builder_shallow_excluding_last_100km_m")} | {"shallow": s["shallow_stretches"]} for s in summary], indent=0))
