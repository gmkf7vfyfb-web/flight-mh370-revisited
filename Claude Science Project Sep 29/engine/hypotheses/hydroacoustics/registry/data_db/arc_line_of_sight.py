#!/usr/bin/env python3
"""
arc_line_of_sight.py - bathymetric line-of-sight screen from the 7th arc (20 S to its southern end) to every
hydroacoustic site in hydro_data.sqlite. Writes table arc_path (one row per site x arc point) and per-site
summary attributes (arc_line_of_sight, arc_blocked_lat, arc_large_attenuation_lat, arc_ridge_partial_lat),
plus check_log rows. Run after build_hydro_data_db.py.

Geometry: 7th arc = spherical small circle, centre 0.570 N 64.252 E, radius 44.501 deg (fitted to 00:19:29
positions; southern end 43.93 S 64.25 E); eastern branch sampled every 0.1 deg latitude from 20.0 S.
Paths: WGS84 geodesics (pyproj), sampled every ~1 km, GEBCO_2026 15" elevation (nearest cell).
Classes (outside the receiver's own approach):
  blocked            land, or water shallower than min(receiver depth, 200 m), more than 20 km from the receiver
  large attenuation  >= 10 km of water shallower than 1,000 m (above the deep sound-channel axis), more than 100 km from the receiver
  ridge (partial)    deep receivers (>= 900 m) only: >= 10 km of water shallower than the hydrophone, more than 100 km from the receiver
  clear              none of the above
This is a geometric screen, not a transmission-loss result.

Usage: python arc_line_of_sight.py --db hydro_data.sqlite --gebco /Users/pete/Downloads/mh370-ocean-data/gebco/grid
"""
import argparse, json, sqlite3
from datetime import datetime, timezone
import numpy as np, pandas as pd, pyproj

C, R = (0.570, 64.252), 44.501
SITES = ["H01W", "H08S", "H08N", "IMOS3315", "IMOS3376", "IMOS3250", "IMOS3274", "IMOS3275",
         "MAD", "NCRO", "WKER", "SWAMS1", "SWAMS2", "SWAMS3", "SSEIR", "NEAMS"]
FEATURES = [  # (name, lat0, lat1, lon0, lon1), most specific first - only used to name the obstacle in the summary text
    ("St Paul Island", -39.0, -38.4, 77.2, 77.9), ("Amsterdam Island", -38.1, -37.6, 77.2, 77.9),
    ("Amsterdam-St Paul plateau", -39.5, -36.5, 76.5, 80.0),
    ("Broken Ridge", -32.3, -29.8, 91.5, 97.5), ("Ninety East Ridge", -31.9, -24.0, 85.5, 90.5),
    ("ridge near 28.5° S 98.6° E", -29.3, -27.8, 97.5, 99.5), ("rise near 33° S 83° E", -35.6, -31.8, 80.0, 85.5),
    ("Cape Leeuwin shelf", -36.0, -33.5, 113.5, 116.5), ("North West Shelf and islands", -22.0, -19.5, 113.5, 117.0),
    ("Exmouth Plateau / North West Shelf edge", -22.5, -14.5, 112.0, 122.0), ("Chagos Bank", -8.0, -4.5, 70.5, 73.0),
    ("Australian continent", -40.0, -10.0, 113.0, 155.0)]
BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dest(lat, lon, az, d):
    la, lo, az, d = map(np.radians, (lat, lon, az, d))
    la2 = np.arcsin(np.sin(la) * np.cos(d) + np.cos(la) * np.sin(d) * np.cos(az))
    lo2 = lo + np.arctan2(np.sin(az) * np.sin(d) * np.cos(la), np.cos(d) - np.sin(la) * np.sin(la2))
    return np.degrees(la2), np.degrees(lo2)


def name_feature(lat, lon):
    for n, a0, a1, o0, o1 in FEATURES:
        if a0 <= lat <= a1 and o0 <= lon <= o1:
            return n
    return f"near {abs(lat):.1f}° S {lon:.1f}° E"


def bands(lats, gap=0.31):
    """Merge sorted (descending) latitudes into 'a-b' bands where consecutive points are within gap deg."""
    lats = sorted(lats, reverse=True)
    out = []
    for x in lats:
        if out and out[-1][1] - x <= gap:
            out[-1][1] = x
        else:
            out.append([x, x])
    return [(a, b) for a, b in out]


def fmt_bands(bs):
    return ", ".join(f"{abs(a):.1f}" if a == b else f"{abs(a):.1f}–{abs(b):.1f}" for a, b in bs) + "° S"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--db", required=True); ap.add_argument("--gebco", required=True)
    a = ap.parse_args()
    gh = json.load(open(f"{a.gebco}/gebco_2026.json"))
    EL = np.fromfile(f"{a.gebco}/{gh['elevation_file']}", dtype="<i2").reshape(gh["nlat"], gh["nlon"])
    zat = lambda la, lo: EL[np.clip(np.rint((la - gh["lat0"]) / gh["step_deg"]).astype(int), 0, gh["nlat"] - 1),
                           np.clip(np.rint((lo - gh["lon0"]) / gh["step_deg"]).astype(int), 0, gh["nlon"] - 1)].astype(float)
    geod = pyproj.Geod(ellps="WGS84")
    az = np.linspace(90, 180, 90001); la, lo = dest(*C, az, R)
    arc = [(la[np.argmin(abs(la - t))], lo[np.argmin(abs(la - t))]) for t in np.round(np.arange(-20, -43.9001, -0.1), 1)]
    arc.append((la.min(), lo[la.argmin()]))
    con = sqlite3.connect(a.db)
    st = pd.read_sql("SELECT site_id, lat, lon, sensor_depth_m FROM site", con).set_index("site_id")
    con.executescript("""DROP TABLE IF EXISTS arc_path;
      CREATE TABLE arc_path (site_id TEXT REFERENCES site(site_id), arc_lat REAL, arc_lon REAL, dist_km REAL, receiver_depth_m REAL,
        land_km REAL, blocking_km REAL, km_shallower_1000m REAL, km_shallower_receiver REAL, shallowest_m REAL,
        obstacle_lat REAL, obstacle_lon REAL, obstacle_km_from_arc REAL, obstacle_name TEXT, class TEXT,
        PRIMARY KEY (site_id, arc_lat));""")
    con.execute("DELETE FROM attribute WHERE key LIKE 'arc_%'"); con.execute("DELETE FROM attribute_key WHERE key LIKE 'arc_%'")
    con.execute("DELETE FROM check_log WHERE check_id LIKE 'L%'")
    for k, d in [("arc_line_of_sight", "Summary of the bathymetric line-of-sight screen from the 7th arc (20 S to its southern end 43.9 S) to this site."),
                 ("arc_blocked_lat", "Arc latitudes (deg S) whose path is blocked by land or water shallower than min(receiver depth, 200 m)."),
                 ("arc_large_attenuation_lat", "Arc latitudes (deg S) whose path has >= 10 km shallower than 1,000 m (large terrain attenuation likely)."),
                 ("arc_ridge_partial_lat", "Deep receivers: arc latitudes (deg S) whose path has >= 10 km shallower than the hydrophone (partial loss)."),
                 ("arc_receiver_depth_m", "Receiver depth used in the arc line-of-sight screen.")]:
        con.execute("INSERT INTO attribute_key (key, entity_type, datatype, unit, description) VALUES (?,?,?,?,?)",
                    (k, "site", "text" if k != "arc_receiver_depth_m" else "real", "m" if k.endswith("_m") else "deg S", d))
    rows, summ = [], {}
    for s in SITES:
        r = st.loc[s]
        seabed = -zat(np.array([r.lat]), np.array([r.lon]))[0]
        rd = 216.0 if s == "IMOS3250" else (float(r.sensor_depth_m) if not s.startswith("IMOS") else float(seabed))
        deep = rd >= 900
        for alat, alon in arc:
            _, _, dist = geod.inv(alon, alat, r.lon, r.lat)
            n = max(int(dist / 1000), 2)
            p = np.array(geod.npts(alon, alat, r.lon, r.lat, n - 1))
            plon, plat = np.r_[alon, p[:, 0], r.lon], np.r_[alat, p[:, 1], r.lat]
            z = zat(plat, plon); step = dist / 1000 / (len(z) - 1); tr = (len(z) - 1 - np.arange(len(z))) * step
            o20, o100 = tr > 20, tr > 100
            blk = ((z >= 0) | (z > -min(rd, 200.0))) & o20
            att = (z > -1000) & o100
            rid = ((z > -rd) & o100) if deep else np.zeros(len(z), bool)
            k1000, krid = att.sum() * step, rid.sum() * step
            cls = "blocked" if blk.any() else ("large attenuation" if k1000 >= 10 else ("ridge (partial)" if krid >= 10 else "clear"))
            m = blk if cls == "blocked" else (att if cls == "large attenuation" else (rid if cls.startswith("ridge") else None))
            ol = oo = ok = None; on = None; shal = None
            if m is not None:
                idx = np.where(m)[0]; k = idx[np.argmax(z[idx])]; ok = k * step; shal = -z[k]
                azf, _, _ = geod.inv(alon, alat, r.lon, r.lat); oo, ol, _ = geod.fwd(alon, alat, azf, ok * 1000); on = name_feature(ol, oo)
            rows.append((s, round(alat, 3), round(alon, 3), round(dist / 1000, 1), rd, round(((z >= 0) & o20).sum() * step, 1),
                         round(blk.sum() * step, 1), round(k1000, 1), None if not deep else round(krid, 1), shal, ol, oo,
                         None if ok is None else round(ok, 1), on, cls))
    con.executemany("INSERT INTO arc_path VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    A = pd.read_sql("SELECT * FROM arc_path", con)
    A["lat1"] = A.arc_lat.round(1)
    tip = abs(A.arc_lat.min())
    RANK = {"blocked": 3, "large attenuation": 2, "ridge (partial)": 1, "clear": 0}
    LABEL = {"blocked": "blocked", "large attenuation": "large attenuation", "ridge (partial)": "ridge above hydrophone depth (partial loss)"}

    def top_names(h, k=2):
        return ", ".join(h.obstacle_name.value_counts().index[:k])

    for s in SITES:
        g = A[A.site_id == s]
        for c, key in [("blocked", "arc_blocked_lat"), ("large attenuation", "arc_large_attenuation_lat"), ("ridge (partial)", "arc_ridge_partial_lat")]:
            gg = g[g["class"] == c]
            if len(gg):
                bs = bands(gg.lat1.tolist())
                note = "; ".join(f"{fmt_bands([b])}: {top_names(gg[(gg.lat1 <= b[0]) & (gg.lat1 >= b[1])])}" for b in bs)
                con.execute("INSERT INTO attribute (entity_type, entity_id, key, value_text, unit, evidence, note, added_utc) VALUES (?,?,?,?,?,?,?,?)",
                            ("site", s, key, fmt_bands(bs), "deg S", "computed (arc_line_of_sight.py)", note, BUILD_UTC))
        lim = g[g["class"] != "clear"]
        if not len(lim):
            text = f"Line of sight to 7th arc 20° S–{tip:.1f}° S (southern end of the arc): clear"
        else:
            items = []
            for c in ["blocked", "large attenuation", "ridge (partial)"]:
                gc = g[g["class"] == c]
                for a0, b0 in (bands(gc.lat1.tolist(), gap=1.01) if len(gc) else []):
                    h = g[(g.lat1 <= a0) & (g.lat1 >= b0)]; hc = h[h["class"] == c]
                    share = len(hc) / len(h)
                    rng = f"{abs(a0):.1f}° S" if a0 == b0 else f"{abs(a0):.1f}–{abs(b0):.1f}° S"
                    q = "" if share > 0.95 else f" at {share * 100:.0f} % of latitudes"
                    items.append((-a0, f"{rng}: {LABEL[c]}{q} ({top_names(hc)})"))
            items = [t for _, t in sorted(items)]
            text = f"Line of sight to 7th arc (20° S–{tip:.1f}° S) limited at " + "; ".join(items) + "; clear elsewhere"
        con.execute("INSERT INTO attribute (entity_type, entity_id, key, value_text, evidence, note, added_utc) VALUES (?,?,?,?,?,?,?)",
                    ("site", s, "arc_line_of_sight", text, "computed (arc_line_of_sight.py)",
                     "GEBCO_2026 15 arc-s, WGS84 geodesics every ~1 km, arc points every 0.1 deg; bands merged within 1 deg; geometric screen, not transmission loss", BUILD_UTC))
        con.execute("INSERT INTO attribute (entity_type, entity_id, key, value_num, unit, evidence, added_utc) VALUES (?,?,?,?,?,?,?)",
                    ("site", s, "arc_receiver_depth_m", float(g.receiver_depth_m.iloc[0]), "m",
                     "FDSN element mean (IMS), Royer Table 1 (OHASISBIO), GEBCO seabed at logger (IMOS; Scott Reef 216 m from metadata)", BUILD_UTC))
        summ[s] = text
    chk = lambda cid, d, ok, det: con.execute("INSERT INTO check_log VALUES (?,?,?,?,?)", (cid, d, "PASS" if ok else "FAIL", det, BUILD_UTC))
    h8n = A[A.site_id == "H08N"]
    nb = int((h8n["class"] == "blocked").sum()); other = h8n[h8n["class"] != "blocked"]
    chk("L01", "Control: Diego Garcia North has no clear path at any arc latitude (Chagos Bank; dropped by ruling 23 Oct 2026)", bool((h8n["class"] != "clear").all()),
        f"{nb} of {len(h8n)} blocked; {len(other)} large attenuation" + (f" ({fmt_bands(bands(other.lat1.tolist()))}, shallowest {other.shallowest_m.min():.0f} m)" if len(other) else ""))
    sr = A[A.site_id == "IMOS3250"].sort_values("arc_lat", ascending=False)
    first_b = sr[sr["class"] == "blocked"].arc_lat.max()
    chk("L02", "Control: Scott Reef blocked south of about 29.6 S (23 Oct 2026 sweep, artifact arc_path_obstacles_20S_40S.csv)", abs(first_b + 29.6) <= 0.2,
        f"first blocked arc latitude {first_b:.1f}")
    chk("L03", "Arc sampling: 20.0 S to southern end", len(A.arc_lat.unique()) == len(arc), f"{len(arc)} arc points; southern end {A.arc_lat.min():.2f} S")
    con.execute("INSERT OR REPLACE INTO meta VALUES ('arc_line_of_sight_built_utc', ?)", (BUILD_UTC,))
    con.commit()
    for s, t in summ.items():
        print(s, "|", t)
    for r_ in con.execute("SELECT check_id, result, detail FROM check_log WHERE check_id LIKE 'L%'"):
        print(*r_)


if __name__ == "__main__":
    main()
