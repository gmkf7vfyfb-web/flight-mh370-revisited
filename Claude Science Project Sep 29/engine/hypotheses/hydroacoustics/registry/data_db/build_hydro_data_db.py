#!/usr/bin/env python3
"""
build_hydro_data_db.py - one SQLite database of the hydroacoustic DATA held by the project
(raw recordings and digitised published data), with site, sensor, dataset, segment, pick,
event and open-ended attribute tables.

Scope: data only (raw waveforms, digitised figures/tables, published picks). Derived results
(noise summaries, detections, likelihoods) stay in the module registry (registry/REGISTRY.json);
every dataset row carries the registry entry id that covers its files.

Inputs (read-only):
  IMOS  = ~/Downloads/mh370-inputs/hydroacoustics/imos          (raw .DAT records, metadata, SHA256SUMS)
  MOD   = <clone>/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics  (module branch)
  FDSN  = ims_stations_all.txt  (EarthScope FDSN station service, net=IM sta=H*, level=station)

Time convention for IMOS: true UTC = logger time - e(t), e(t) linear between 'system clock set 1'
and 'system clock set 2' of the Curtin metadata (convention A, accepted by the module's clock test
results-data/imos1d/clock_test.json: CMST 01:33:44 event reproduced to -0.24 s).

Usage: python build_hydro_data_db.py --mod <MOD> --imos <IMOS> --fdsn <file> --out hydro_data.sqlite [--no-hash]
"""
import argparse, glob, hashlib, io, json, os, re, sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import numpy as np
import pandas as pd

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SCHEMA_VERSION = "hydro-data-db v1"

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE source (
  source_id TEXT PRIMARY KEY, short_name TEXT NOT NULL, citation TEXT, year INTEGER,
  doi_or_url TEXT, local_copy TEXT, notes TEXT);
CREATE TABLE site (
  site_id TEXT PRIMARY KEY, name TEXT NOT NULL, network TEXT, kind TEXT,
  lat REAL, lon REAL, water_depth_m REAL, sensor_depth_m REAL,
  position_source_id TEXT REFERENCES source(source_id), position_note TEXT, region TEXT, notes TEXT);
CREATE TABLE sensor (
  sensor_id TEXT PRIMARY KEY, site_id TEXT NOT NULL REFERENCES site(site_id),
  lat REAL, lon REAL, depth_m REAL, sample_rate_hz REAL, epoch_start TEXT, description TEXT,
  position_source_id TEXT REFERENCES source(source_id));
CREATE TABLE dataset (
  dataset_id TEXT PRIMARY KEY, title TEXT NOT NULL,
  site_id TEXT REFERENCES site(site_id),
  source_id TEXT REFERENCES source(source_id),
  data_form TEXT NOT NULL,            -- raw_waveform | digitised_trace | digitised_spectrogram | digitised_band_series | digitised_table | digitised_picks | derived_from_digitised | raster_copy
  quantity TEXT, units TEXT,
  context TEXT NOT NULL,             -- 'MH370 7-8 Mar 2014' or 'calibration: <case>'
  t_start_utc TEXT, t_end_utc TEXT, time_basis TEXT,
  sample_rate_hz REAL, resolution_note TEXT,
  band_lo_hz REAL, band_hi_hz REAL, band_basis TEXT,
  continuity TEXT,                   -- continuous | duty-cycled | separate windows | point picks | no time axis
  n_segments INTEGER, covered_s REAL, span_s REAL, duty_fraction REAL,
  path TEXT, registry_entry_id TEXT, status TEXT, caveat TEXT);
CREATE TABLE segment (
  dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id), seq INTEGER NOT NULL,
  label TEXT, t_start_utc TEXT, t_end_utc TEXT, duration_s REAL,
  t_start_logger TEXT, clock_err_s REAL, sample_rate_hz REAL, n_samples INTEGER,
  band_lo_hz REAL, band_hi_hz REAL, role TEXT, file_path TEXT, bytes INTEGER,
  sha256 TEXT, sha256_check TEXT, same_file_in TEXT, PRIMARY KEY (dataset_id, seq));
CREATE TABLE event (
  event_id TEXT PRIMARY KEY, source_id TEXT REFERENCES source(source_id), label TEXT, event_class TEXT,
  origin_utc TEXT, lat REAL, lon REAL, err_lat_deg REAL, err_lon_deg REAL, err_time_s REAL,
  n_hydrophones INTEGER, note TEXT);
CREATE TABLE pick (
  pick_id INTEGER PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
  site_id TEXT REFERENCES site(site_id), kind TEXT, label TEXT,
  t_utc TEXT, t_end_utc TEXT, bearing_deg REAL, value REAL, value_unit TEXT,
  event_id TEXT REFERENCES event(event_id), note TEXT);
CREATE TABLE attribute_key (
  key TEXT PRIMARY KEY, entity_type TEXT, datatype TEXT, unit TEXT, description TEXT NOT NULL);
CREATE TABLE attribute (
  attr_id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
  key TEXT NOT NULL REFERENCES attribute_key(key), value_text TEXT, value_num REAL, unit TEXT,
  source_id TEXT REFERENCES source(source_id), evidence TEXT, note TEXT, added_utc TEXT);
CREATE TABLE imported_table (
  table_name TEXT PRIMARY KEY, source_file TEXT, sha256 TEXT, n_rows INTEGER, n_cols INTEGER,
  header_comment TEXT, dataset_id TEXT REFERENCES dataset(dataset_id));
CREATE TABLE file_ref (
  file_path TEXT PRIMARY KEY, dataset_id TEXT REFERENCES dataset(dataset_id), kind TEXT,
  bytes INTEGER, sha256 TEXT, note TEXT);
CREATE TABLE check_log (
  check_id TEXT PRIMARY KEY, description TEXT, result TEXT, detail TEXT, run_utc TEXT);
CREATE INDEX ix_seg_t ON segment(t_start_utc);
CREATE INDEX ix_pick_t ON pick(t_utc);
CREATE INDEX ix_attr ON attribute(entity_type, entity_id, key);
"""

VIEWS = """
CREATE VIEW v_dataset_summary AS
SELECT d.dataset_id, d.site_id, s.name AS site_name, d.context, d.data_form, d.title,
       d.t_start_utc, d.t_end_utc, d.continuity, d.n_segments, d.duty_fraction,
       d.band_lo_hz, d.band_hi_hz, d.band_basis, d.sample_rate_hz, d.resolution_note,
       d.source_id, d.registry_entry_id, d.status, d.caveat
FROM dataset d LEFT JOIN site s USING (site_id);
CREATE VIEW v_site_holdings AS
SELECT s.site_id, s.name, s.network, s.lat, s.lon, s.region,
       COUNT(d.dataset_id) AS n_datasets,
       SUM(d.data_form = 'raw_waveform') AS n_raw,
       SUM(d.data_form <> 'raw_waveform') AS n_digitised,
       MIN(d.t_start_utc) AS first_utc, MAX(d.t_end_utc) AS last_utc
FROM site s LEFT JOIN dataset d USING (site_id) GROUP BY s.site_id;
CREATE VIEW v_picks_by_site AS
SELECT p.site_id, p.dataset_id, COUNT(*) AS n_picks, MIN(p.t_utc) AS first_utc, MAX(p.t_utc) AS last_utc
FROM pick p GROUP BY p.site_id, p.dataset_id;
"""

# ----------------------------------------------------------------------------------------------
def sha256_file(path, bufsize=8 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def iso(ts):
    if ts is None:
        return None
    ts = pd.Timestamp(ts)
    if ts is pd.NaT:
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    ts = ts.tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def dm(s):
    m = re.match(r"\s*(\d+)\s*deg\s*([\d.]+)'\s*([NSEW])", s)
    v = int(m.group(1)) + float(m.group(2)) / 60
    return -v if m.group(3) in "SW" else v


def parse_meta(imos):
    out = {}
    for mf in ["MH370/3315_3250_3376__MetaData.txt", "Portland_MH370/MetaData_3274_3275.txt"]:
        txt = open(os.path.join(imos, mf), errors="replace").read().replace("\r", "")
        for block in txt.split("Curtin ID")[1:]:
            lines = ("Curtin ID" + block).splitlines()
            kv = {ln[:40].strip(): ln[40:].strip() for ln in lines if len(ln) > 40}
            cid = kv["Curtin ID"]
            c1, c2 = kv["system clock set 1"].split(), kv["system clock set 2"].split()
            out[cid] = dict(kv=kv, metafile=mf, lat=dm(kv["Latitude (WGS84)"]), lon=dm(kv["Longitude (WGS84)"]),
                            clock1=(pd.Timestamp(f"{c1[0]} {c1[1]}", tz="UTC"), float(c1[2])),
                            clock2=(pd.Timestamp(f"{c2[0]} {c2[1]}", tz="UTC"), float(c2[2])))
    return out


def clock_err(meta, t):
    (t1, e1), (t2, e2) = meta["clock1"], meta["clock2"]
    return e1 + (e2 - e1) * (t - t1).total_seconds() / (t2 - t1).total_seconds()


def dat_header(path):
    """Same reading as prepare/imos_preregistration.header(): logger-clock start from footer 'First Data'."""
    with open(path, "rb") as f:
        hdr = [f.readline().decode("latin1").rstrip() for _ in range(5)]
        start = f.tell()
        f.seek(-1000, 2)
        tail = f.read().decode("latin1")
        size = f.seek(0, 2)
    fs = int(re.search(r"Sample Rate (\d+)", hdr[2]).group(1))
    first = re.search(r"First Data-(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d)", tail).group(1)
    footer_bytes = 1000 - tail.index("Record")
    n = (size - footer_bytes - 2 - start) // 2
    filt = hdr[3]
    lf = re.search(r"LF=(\d+)", filt); hf = re.search(r"HF=(\d+)", filt)
    return dict(fs=fs, start=pd.Timestamp(first.replace("/", "-"), tz="UTC"), n=int(n), filter0=filt,
                lf=float(lf.group(1)) if lf else None, hf=float(hf.group(1)) if hf else None, bytes=size)


def merged_cover(intervals, tol_s=2.0):
    """Union length (s) and number of separate windows of [start, end] ISO intervals (gaps <= tol_s joined)."""
    iv = sorted((pd.Timestamp(a), pd.Timestamp(b)) for a, b in intervals)
    m = []
    for a, b in iv:
        if m and a <= m[-1][1] + pd.Timedelta(seconds=tol_s):
            m[-1][1] = max(m[-1][1], b)
        else:
            m.append([a, b])
    return sum((b - a).total_seconds() for a, b in m), len(m)


def norm_station(s):
    """Map station spellings in the sources to site ids: H01W1/H01W-2 -> H01W, H08S1 -> H08S, SWAMS-3 -> SWAMS3."""
    s = s.upper().strip()
    for tri in ("H01W", "H08S", "H08N"):
        if s.startswith(tri):
            return tri
    return s.replace("-", "")


def read_csv_commented(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    com = [l for l in lines if l.startswith("#")]
    body = "\n".join(l for l in lines if not l.startswith("#"))
    df = pd.read_csv(io.StringIO(body)) if body.strip() else pd.DataFrame()
    return df, "\n".join(com)


# ----------------------------------------------------------------------------------------------
class DB:
    def __init__(self, path):
        if os.path.exists(path):
            os.remove(path)
        self.con = sqlite3.connect(path)
        self.con.executescript(SCHEMA)
        self.checks = []

    def ins(self, table, row):
        cols = ",".join(row.keys())
        q = ",".join("?" * len(row))
        self.con.execute(f"INSERT INTO {table} ({cols}) VALUES ({q})", [None if (isinstance(v, float) and np.isnan(v)) else v for v in row.values()])

    def ins_many(self, table, rows):
        if not rows:
            return
        cols = list(rows[0].keys())
        self.con.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                             [[(None if (isinstance(r.get(c), float) and np.isnan(r.get(c))) else r.get(c)) for c in cols] for r in rows])

    def attr(self, et, eid, key, value=None, unit=None, source_id=None, evidence="stated in source", note=None):
        isnum = isinstance(value, (int, float, np.floating, np.integer)) and not isinstance(value, bool)
        self.ins("attribute", dict(entity_type=et, entity_id=eid, key=key, value_text=None if isnum else (None if value is None else str(value)),
                                   value_num=float(value) if isnum else None, unit=unit, source_id=source_id,
                                   evidence=evidence, note=note, added_utc=BUILD_UTC))

    def check(self, cid, desc, ok, detail):
        self.checks.append((cid, desc, ok, detail))
        self.ins("check_log", dict(check_id=cid, description=desc, result="PASS" if ok else "FAIL",
                                   detail=detail, run_utc=BUILD_UTC))


ATTRIBUTE_KEYS = [
    ("hydrophone_sensitivity_db", "site|sensor", "real", "dB re V^2/Pa^2 (as printed)", "Hydrophone sensitivity as printed in the source."),
    ("system_gain_file", "site", "text", None, "Curtin calibration record named in the logger metadata ('system gain file')."),
    ("hydrophone_serial", "site", "text", None, "Hydrophone serial number from the logger metadata."),
    ("clock_set_1", "site", "text", "UTC, s", "Logger clock set 1: time and clock error (s) as printed."),
    ("clock_set_2", "site", "text", "UTC, s", "Logger clock set 2: time and clock error (s) as printed."),
    ("clock_drift_s_per_day", "site", "real", "s/day", "Mean logger clock drift from the metadata."),
    ("clock_err_on_8_march_s", "site", "real", "s", "Logger clock error interpolated to 8 Mar 2014 12:00 UTC (linear between clock sets)."),
    ("clock_convention", "site|dataset", "text", None, "How logger time is converted to UTC."),
    ("record_length_s", "site", "real", "s", "Mean record length from the logger metadata."),
    ("record_interval_min", "site", "real", "min", "Record repeat interval from the logger metadata."),
    ("deployment_set", "site", "text", None, "Curtin deployment set description."),
    ("deployment_first_sample_utc", "site", "text", "UTC", "Start of first sample of the deployment (metadata)."),
    ("deployment_last_sample_utc", "site", "text", "UTC", "Start of last sample of the deployment (metadata)."),
    ("hardware_highpass_hz", "site|dataset", "real", "Hz", "Hardware high-pass corner of the recording chain (record header LF)."),
    ("hardware_lowpass_hz", "site|dataset", "real", "Hz", "Hardware low-pass (anti-alias) corner (record header HF)."),
    ("sensor_band_nominal", "site|sensor", "text", "Hz", "Nominal sensor band as printed in the station metadata."),
    ("instrument_response_file", "site|sensor", "text", None, "Instrument response file held in the module data tree."),
    ("conversion_factor", "site", "text", None, "Count-to-pressure conversion factors as printed (Royer 2016 Table 3)."),
    ("path_note", "site", "text", None, "Propagation-path note for this site with respect to the 7th arc."),
    ("author_processing", "dataset", "text", None, "Filtering or processing the author states was applied before plotting."),
    ("digitisation_method", "dataset", "text", None, "How the digitised values were extracted."),
    ("timing_caveat", "dataset|site", "text", None, "Known timing issue that changes how the time axis is read."),
    ("amplitude_caveat", "dataset", "text", None, "Known amplitude/scale issue."),
    ("publication_page", "dataset", "text", None, "Page/figure/table in the source publication."),
    ("site_status_in_source", "site", "text", None, "Station status as printed in the source (e.g. recorded / lost on recovery)."),
]


# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", required=True)
    ap.add_argument("--imos", required=True)
    ap.add_argument("--fdsn", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--git-head", default="")
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()
    MOD, IMOS = a.mod, a.imos
    db = DB(a.out)
    for k in ATTRIBUTE_KEYS:
        db.ins("attribute_key", dict(key=k[0], entity_type=k[1], datatype=k[2], unit=k[3], description=k[4]))

    # ------------------------------------------------------------------ sources
    SOURCES = [
        ("imos_curtin_2014", "IMOS / Curtin CMST passive acoustic loggers", None,
         "https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/ (background days); MH370 release download (event day)",
         "INPUTS:imos", "Raw .DAT records and Curtin metadata files. Retrieved 2026-10-09 (RETRIEVED_UTC.txt)."),
        ("fdsn_earthscope", "FDSN station service (EarthScope), network IM", None,
         "https://service.earthscope.org/fdsnws/station/1/query?net=IM&sta=H*", "MOD:data/stations.csv; ims_stations_all.txt",
         "IMS hydrophone element positions and depths. stations.csv retrieved 2026-10-07; station-level list retrieved at build."),
        ("kadri2024", "Kadri 2024, Sci. Rep. 14:10102", 2024, "doi:10.1038/s41598-024-60529-1", "PMC full text; Drive copy",
         "Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea: revisiting MH370."),
        ("kadri2024_s1", "Kadri 2024, Sci. Rep. 14:10102, Supplementary S1", 2024, "doi:10.1038/s41598-024-60529-1", None, None),
        ("kadri2019", "Kadri 2019, Sci. Rep. 9:912", 2019, "doi:10.1038/s41598-018-37626-z", "EX:sources/open-access-fetched-2026-10-22", None),
        ("kadri2017", "Kadri et al. 2017, Sci. Rep. 7:13949", 2017, None, None, None),
        ("royer2016", "Royer 2016, OHASISBIO report LDO-201608", 2016, None, "artifact royer-2016-LDO-201608.pdf (sha256 2e7190b96c7bb774...)", None),
        ("cmst2014", "CMST report 2014-30 (Curtin University)", 2014, None, "pdf sha256 1c19b353562ff4cd...", "Curtin analysis of IMOS and IMS records for MH370."),
        ("blackman2004", "Blackman et al. UCRL-TR-207323 (2004)", 2004, None, None, "2001 airgun calibration shots at H01 and H08."),
        ("brown2026", "Brown et al. 2026, Icarus", 2026, None, "pdf sha256 4b45d454bba9e563...", "Fireball hydroacoustic cases."),
        ("metz2023", "Metz, Obana & Fukao 2023, PAGEOPH 180:1343", 2023, None, "EX:sources/Metz_Obana_Fukao_2023_...pdf", "F-35A crash arrival at H11."),
        ("nielsen2021", "Nielsen et al. 2021, PAAG 178", 2021, None, None, "ARA San Juan and depth charge."),
        ("vergoz2021", "Vergoz et al. 2021, PAAG 178", 2021, None, None, "ARA San Juan."),
        ("duncan2023", "Duncan & Dall'Osto 2023", 2023, None, None, "Modelled signal strength along paths from HA01."),
    ]
    for s in SOURCES:
        db.ins("source", dict(source_id=s[0], short_name=s[1], year=s[2], doi_or_url=s[3], local_copy=s[4], notes=s[5], citation=s[1]))

    # ------------------------------------------------------------------ sites: IMS (FDSN)
    st = pd.read_csv(os.path.join(MOD, "data/stations.csv"), comment="#")
    fd = pd.read_csv(a.fdsn, sep="|")
    fd.columns = [c.strip("# ").strip() for c in fd.columns]
    fd = fd[(fd.StartTime <= "2014-03-08") & (fd.EndTime.isna() | (fd.EndTime.astype(str) > "2014-03-08"))]
    fd = fd[fd.Elevation < 0]  # hydrophone elements (state-of-health sites have elevation >= 0)
    IMS_NAMES = {"H01W": "Cape Leeuwin", "H08S": "Diego Garcia South", "H08N": "Diego Garcia North",
                 "H11N": "Wake Island North", "H11S": "Wake Island South", "H10N": "Ascension Island North",
                 "H10S": "Ascension Island South", "H04S": "Crozet Islands South", "H03S": "Juan Fernandez South",
                 "H03N": "Juan Fernandez North"}
    REGION = {"H01W": "Indian Ocean", "H08S": "Indian Ocean", "H08N": "Indian Ocean", "H04S": "Indian Ocean",
              "H11N": "Pacific Ocean", "H11S": "Pacific Ocean", "H03S": "Pacific Ocean", "H03N": "Pacific Ocean",
              "H10N": "Atlantic Ocean", "H10S": "Atlantic Ocean"}
    fd["triad"] = fd.Station.str[:4]
    for tri, name in IMS_NAMES.items():
        el = fd[fd.triad == tri]
        if len(el):
            lat, lon, dep = el.Latitude.mean(), el.Longitude.mean(), (-el.Elevation).mean()
            psrc, pnote = "fdsn_earthscope", f"mean of {len(el)} hydrophone elements valid on 2014-03-08"
        else:
            lat = lon = dep = None
            psrc, pnote = None, "position not in the held files or the FDSN EarthScope station list (searched at build)"
        db.ins("site", dict(site_id=tri, name=name, network="IMS (CTBTO)", kind="IMS hydrophone triad", lat=lat, lon=lon,
                            water_depth_m=None, sensor_depth_m=dep, position_source_id=psrc, position_note=pnote,
                            region=REGION[tri], notes=None))
        for _, r in el.iterrows():
            srow = st[st.element == r.Station]
            db.ins("sensor", dict(sensor_id=r.Station, site_id=tri, lat=r.Latitude, lon=r.Longitude, depth_m=-r.Elevation,
                                  sample_rate_hz=float(srow.sample_rate_hz.iloc[0]) if len(srow) else None,
                                  epoch_start=r.StartTime, description=(srow.sensor.iloc[0] if len(srow) else r.SiteName),
                                  position_source_id="fdsn_earthscope"))
            if len(srow):
                db.attr("sensor", r.Station, "sensor_band_nominal", srow.sensor.iloc[0], source_id="fdsn_earthscope")
    m = st.merge(fd, left_on="element", right_on="Station")
    dmax = float(np.max(np.hypot(m.latitude_deg - m.Latitude, (m.longitude_deg - m.Longitude) * np.cos(np.radians(m.Latitude)))) * 111.2e3)
    db.check("C01", "IMS element positions: module stations.csv against FDSN station list", dmax < 5,
             f"{len(m)} elements matched; max horizontal difference {dmax:.1f} m")
    for f in sorted(glob.glob(os.path.join(MOD, "data/ims_response_2003/*.xml"))) + [os.path.join(MOD, "data/ims_response_H08S1.xml")]:
        tri = os.path.basename(f).replace("ims_response_", "")[:4]
        db.attr("site", tri, "instrument_response_file", os.path.relpath(f, MOD), source_id="fdsn_earthscope",
                evidence="file held", note="2003 epoch response" if "2003" in f else "current epoch response")

    # ------------------------------------------------------------------ sites: OHASISBIO (Royer Table 1)
    rs = pd.read_csv(os.path.join(MOD, "results-data/digitised/royer-2016/royer_stations.csv"))
    sens = pd.read_csv(os.path.join(MOD, "results-data/digitised/royer-2016/royer_sensitivity.csv"))
    for _, r in rs[rs.network == "OHASISBIO"].iterrows():
        db.ins("site", dict(site_id=r.station, name=r.station, network="OHASISBIO", kind="autonomous hydrophone (moored)",
                            lat=r.lat_deg, lon=r.lon_deg, water_depth_m=r.site_depth_m, sensor_depth_m=r.hydrophone_depth_m,
                            position_source_id="royer2016", position_note="Royer 2016 Table 1 (digitised text layer)",
                            region="Indian Ocean", notes=None if pd.isna(r.note) else r.note))
        db.attr("site", r.station, "site_status_in_source", r.status, source_id="royer2016")
        s2 = sens[sens.site == r.station]
        if len(s2):
            db.attr("site", r.station, "conversion_factor",
                    f"{s2.uV_per_count.iloc[0]} uV/count; {s2.sensitivity_dB_re_1uPa_per_V.iloc[0]} dB re 1 uPa/V", source_id="royer2016")
    rr = rs[rs.network != "OHASISBIO"].merge(fd, left_on="station", right_on="Station")
    dd = (np.hypot(rr.lat_deg - rr.Latitude, (rr.lon_deg - rr.Longitude) * np.cos(np.radians(rr.Latitude))) * 111.2e3)
    db.check("C02", "IMS element positions: Royer 2016 Table 1 against FDSN (recorded; FDSN used)", True,
             f"{len(rr)} elements; horizontal differences {dd.min():.0f}-{dd.max():.0f} m; Royer prints hydrophone depth 800 m, FDSN {(-rr.Elevation).min():.0f}-{(-rr.Elevation).max():.0f} m")

    # ------------------------------------------------------------------ sites: IMOS loggers
    meta = parse_meta(IMOS)
    prereg = json.load(open(os.path.join(MOD, "data/imos/preregistration.json")))
    IMOS_NAME = {"3315": "Perth Canyon logger 3315", "3376": "Perth Canyon logger 3376", "3250": "Scott Reef logger 3250",
                 "3274": "Portland logger 3274", "3275": "Portland logger 3275"}
    noon = pd.Timestamp("2014-03-08 12:00", tz="UTC")
    pos_diff = []
    for cid, mm in meta.items():
        kv = mm["kv"]
        wd = kv.get("water depth (m)", ""); rd = kv.get("receiver depth (m)", "")
        isnum = lambda s: bool(re.match(r"^[\d.]+$", s))
        db.ins("site", dict(site_id=f"IMOS{cid}", name=IMOS_NAME[cid], network="IMOS (Curtin CMST)",
                            kind="seabed logger (duty-cycled)", lat=mm["lat"], lon=mm["lon"],
                            water_depth_m=float(wd) if isnum(wd) else None, sensor_depth_m=float(rd) if isnum(rd) else None,
                            position_source_id="imos_curtin_2014", position_note=f"Curtin metadata {mm['metafile']}",
                            region="Indian Ocean" if cid not in ("3274", "3275") else "Southern Ocean (off Portland, Victoria)",
                            notes=None if isnum(wd) else "Water and receiver depth 'not noted' in the metadata"))
        E = f"IMOS{cid}"
        db.attr("site", E, "deployment_set", kv["Set details"], source_id="imos_curtin_2014")
        db.attr("site", E, "hydrophone_sensitivity_db", float(kv["hydrophone sensitivity (dB re V^2/Pa^2)"]),
                unit="dB re V^2/Pa^2 (as printed)", source_id="imos_curtin_2014")
        db.attr("site", E, "hydrophone_serial", kv["hydrophone serial number"], source_id="imos_curtin_2014")
        db.attr("site", E, "system_gain_file", kv["system gain file"], source_id="imos_curtin_2014")
        db.attr("site", E, "clock_set_1", kv["system clock set 1"], source_id="imos_curtin_2014")
        db.attr("site", E, "clock_set_2", kv["system clock set 2"], source_id="imos_curtin_2014")
        dr = re.search(r"\(\s*(-?[\d.]+)\)", kv["clock drift (s) (s/day)"])
        db.attr("site", E, "clock_drift_s_per_day", float(dr.group(1)), unit="s/day", source_id="imos_curtin_2014")
        db.attr("site", E, "clock_err_on_8_march_s", round(clock_err(mm, noon), 2), unit="s", evidence="computed at build",
                note="linear between clock sets")
        rl = kv["mean sample length/increment (s/min)"].split("/")
        db.attr("site", E, "record_length_s", float(rl[0]), unit="s", source_id="imos_curtin_2014")
        db.attr("site", E, "record_interval_min", float(rl[1]), unit="min", source_id="imos_curtin_2014")
        db.attr("site", E, "deployment_first_sample_utc", kv["start first sample (UTC)"], source_id="imos_curtin_2014")
        db.attr("site", E, "deployment_last_sample_utc", kv["start last sample (UTC)"], source_id="imos_curtin_2014")
        db.attr("site", E, "clock_convention", "true UTC = logger time - e(t), e linear between clock sets (convention A)",
                evidence="module test results-data/imos1d/clock_test.json (verdict A, -0.24 s against CMST 01:33:44)")
        p = prereg["loggers"].get(cid, {})
        if p.get("path_flag"):
            db.attr("site", E, "path_note", p["path_flag"], evidence="module preregistration.json")
        if p:
            pos_diff.append(np.hypot(p["lat"] - mm["lat"], (p["lon"] - mm["lon"]) * np.cos(np.radians(mm["lat"]))) * 111.2e3)
    db.attr("site", "IMOS3250", "path_note", "North West Shelf in the path from the 7th arc", evidence="wording ruled by Pete 22 Oct 2026")
    db.check("C17", "IMOS logger positions: metadata parse against module preregistration.json", max(pos_diff) < 5,
             f"{len(pos_diff)} loggers; max difference {max(pos_diff):.1f} m")

    # ------------------------------------------------------------------ IMOS raw datasets
    rec = pd.read_csv(os.path.join(MOD, "data/imos/recordings.csv"))
    rec["start_logger"] = pd.to_datetime(rec.start_logger, utc=True)
    hash_jobs, seg_rows, imos_ds = [], [], {}
    for cid in ["3315", "3376", "3250", "3274", "3275"]:
        r = rec[rec.logger.astype(str) == cid].sort_values("start_logger").reset_index(drop=True)
        ds = f"imos{cid}_mh370_day"
        rows = []
        for i, x in r.iterrows():
            e = clock_err(meta[cid], x.start_logger)
            t0 = x.start_logger - pd.Timedelta(seconds=e)
            fpath = os.path.join(IMOS, x.file)
            lf = float(re.search(r"LF=(\d+)", x.filter0).group(1)); hf = float(re.search(r"HF=(\d+)", x.filter0).group(1))
            rows.append(dict(dataset_id=ds, seq=i, label=os.path.basename(x.file), t_start_utc=iso(t0),
                             t_end_utc=iso(t0 + pd.Timedelta(seconds=x.dur_s)), duration_s=float(x.dur_s),
                             t_start_logger=iso(x.start_logger), clock_err_s=round(e, 3), sample_rate_hz=float(x.fs),
                             n_samples=int(x.n_samples), band_lo_hz=lf, band_hi_hz=hf,
                             role={"B": "pre-registered background", "S": "pre-registered signal window"}.get(x.role, "other"),
                             file_path="INPUTS:imos/" + x.file, bytes=os.path.getsize(fpath), sha256=x.sha256, sha256_check=None))
            hash_jobs.append((ds, i, fpath, x.sha256))
        seg_rows += rows
        imos_ds[cid] = (ds, rows)
    cal_rows = []
    for d in ["MH370/Calibration", "Portland_MH370/calibration"]:
        for f in sorted(glob.glob(os.path.join(IMOS, d, "*.DAT"))):
            h = dat_header(f)
            cal_rows.append(dict(dataset_id="imos_calibration_records", seq=len(cal_rows), label=os.path.basename(f),
                                 t_start_utc=None, t_end_utc=None, duration_s=h["n"] / h["fs"], t_start_logger=iso(h["start"]),
                                 clock_err_s=None, sample_rate_hz=h["fs"], n_samples=h["n"], band_lo_hz=h["lf"], band_hi_hz=h["hf"],
                                 role="calibration record", file_path="INPUTS:imos/" + os.path.relpath(f, IMOS),
                                 bytes=h["bytes"], sha256=None, sha256_check=None))
            hash_jobs.append(("imos_calibration_records", len(cal_rows) - 1, f, None))
    bg_rows = {}
    for cid in ["3376", "3274", "3250"]:
        sums = {}
        for ln in open(os.path.join(IMOS, "background", cid, "SHA256SUMS.txt")):
            if ln.strip():
                hsh, fn = ln.strip().split(None, 1)
                sums[os.path.basename(fn.lstrip("*"))] = hsh
        files = sorted(glob.glob(os.path.join(IMOS, "background", cid, "2014*", "*.DAT")))
        rows = []
        for f in files:
            h = dat_header(f)
            e = clock_err(meta[cid], h["start"])
            t0 = h["start"] - pd.Timedelta(seconds=e)
            rows.append(dict(dataset_id=f"imos{cid}_background", seq=len(rows), label=os.path.basename(f), t_start_utc=iso(t0),
                             t_end_utc=iso(t0 + pd.Timedelta(seconds=h["n"] / h["fs"])), duration_s=h["n"] / h["fs"],
                             t_start_logger=iso(h["start"]), clock_err_s=round(e, 3), sample_rate_hz=h["fs"], n_samples=h["n"],
                             band_lo_hz=h["lf"], band_hi_hz=h["hf"], role="14-day background",
                             file_path="INPUTS:imos/" + os.path.relpath(f, IMOS), bytes=h["bytes"],
                             sha256=sums.get(os.path.basename(f)), sha256_check=None))
            hash_jobs.append((f"imos{cid}_background", len(rows) - 1, f, sums.get(os.path.basename(f))))
        bg_rows[cid] = rows
        db.check(f"C03_{cid}", f"IMOS {cid} background: files on disk equal SHA256SUMS lines", len(files) == len(sums),
                 f"{len(files)} files, {len(sums)} checksum lines")

    if not a.no_hash:
        with ThreadPoolExecutor(max_workers=12) as ex:
            hashes = list(ex.map(sha256_file, [j[2] for j in hash_jobs], chunksize=8))
    else:
        hashes = [None] * len(hash_jobs)
    hmap = {(j[0], j[1]): (h, j[3]) for j, h in zip(hash_jobs, hashes)}
    n_ok = n_bad = n_new = 0
    for rows in [seg_rows, cal_rows] + list(bg_rows.values()):
        for r in rows:
            h, exp = hmap[(r["dataset_id"], r["seq"])]
            if h is None:
                r["sha256_check"] = "not run"
            elif exp is None:
                r["sha256"] = h; r["sha256_check"] = "computed at build"; n_new += 1
            elif h == exp:
                r["sha256_check"] = "match"; n_ok += 1
            else:
                r["sha256_check"] = f"MISMATCH (file {h[:12]})"; n_bad += 1
    db.check("C04", "IMOS raw files: SHA-256 recomputed against recordings.csv / SHA256SUMS", n_bad == 0 and not a.no_hash,
             f"{n_ok} match, {n_bad} mismatch, {n_new} computed without a reference (calibration records)")

    def add_imos_dataset(ds, cid, title, rows, ctx, note):
        t0 = min(r["t_start_utc"] for r in rows); t1 = max(r["t_end_utc"] for r in rows)
        cov = sum(r["duration_s"] for r in rows)
        span = (pd.Timestamp(t1) - pd.Timestamp(t0)).total_seconds()
        fs = sorted({r["sample_rate_hz"] for r in rows}); lo = sorted({r["band_lo_hz"] for r in rows}); hi = sorted({r["band_hi_hz"] for r in rows})
        db.ins("dataset", dict(dataset_id=ds, title=title, site_id=f"IMOS{cid}", source_id="imos_curtin_2014", data_form="raw_waveform",
                               quantity="hydrophone voltage (counts; volts = counts*5/65536)", units="counts", context=ctx,
                               t_start_utc=t0, t_end_utc=t1, time_basis="UTC from logger clock, drift-corrected (convention A)",
                               sample_rate_hz=fs[0], resolution_note=f"{len(rows)} records of about {np.median([r['duration_s'] for r in rows]):.1f} s, one every 15 min",
                               band_lo_hz=lo[0], band_hi_hz=hi[0], band_basis="logger hardware filter (record header Filter 0: LF high-pass, HF low-pass corner)",
                               continuity="duty-cycled", n_segments=len(rows), covered_s=cov, span_s=span, duty_fraction=cov / span if span else None,
                               path="INPUTS:imos", registry_entry_id="in.imos_raw", status="CURRENT", caveat=note))
        db.ins_many("segment", rows)
        db.attr("dataset", ds, "hardware_highpass_hz", lo[0], unit="Hz", source_id="imos_curtin_2014", evidence="record header")
        db.attr("dataset", ds, "hardware_lowpass_hz", hi[0], unit="Hz", source_id="imos_curtin_2014", evidence="record header")
        db.check(f"C05_{ds}", f"{ds}: one sample rate and one filter setting in all records", len(fs) == 1 and len(lo) == 1 and len(hi) == 1,
                 f"fs {fs}, LF {lo}, HF {hi}")

    for cid, (ds, rows) in imos_ds.items():
        add_imos_dataset(ds, cid, f"{IMOS_NAME[cid]}: raw records around 8 March 2014", rows, "MH370 7-8 Mar 2014",
                         "Duty-cycled: an arrival can fall between records. Below 8 Hz the hardware high-pass removes signal: 2-5 and 5-10 Hz band levels are not ambient noise.")
    for cid, rows in bg_rows.items():
        add_imos_dataset(f"imos{cid}_background", cid, f"{IMOS_NAME[cid]}: 14-day background (1-7 and 9-15 March 2014)", rows,
                         "background for MH370 7-8 Mar 2014", "Pre-registered background days (commit eb83b31). Same duty cycle as the event day.")
    db.ins("dataset", dict(dataset_id="imos_calibration_records", title="IMOS logger calibration records", site_id=None,
                           source_id="imos_curtin_2014", data_form="raw_waveform", quantity="calibration signal", units="counts",
                           context="instrument calibration", time_basis="logger clock", continuity="separate windows",
                           n_segments=len(cal_rows), path="INPUTS:imos/MH370/Calibration; INPUTS:imos/Portland_MH370/calibration",
                           registry_entry_id="in.imos_raw", status="CURRENT", caveat="Used for system gain (results-data/imos1d/calibration_gain.csv)."))
    db.ins_many("segment", cal_rows)
    for cid, (ds, rows) in imos_ds.items():
        t = pd.to_datetime([r["t_start_utc"] for r in rows])
        gaps = np.diff(t.values).astype("timedelta64[ms]").astype(float) / 1000
        db.check(f"C06_{cid}", f"IMOS {cid} event-day records: start spacing (expected about 900 s)", abs(np.median(gaps) - 900) < 5,
                 f"spacing median {np.median(gaps):.1f} s, min {gaps.min():.1f} s, max {gaps.max():.1f} s; n={len(rows)}")
    n_disk = sum(len(glob.glob(os.path.join(IMOS, d, "*.DAT"))) for d in
                 ["MH370/3315_PerthCanyon", "MH370/3376_PerthCanyon", "MH370/3250_ScottReef", "Portland_MH370/3274_Portland", "Portland_MH370/3275_Portland"])
    db.check("C07", "IMOS event-day: recordings.csv rows equal .DAT files on disk", n_disk == len(rec), f"{len(rec)} rows, {n_disk} files")
    offs = []
    for r in seg_rows + [x for v in bg_rows.values() for x in v]:
        try:
            u = int(r["label"].split(".")[0], 16)
            offs.append((pd.Timestamp(r["t_start_logger"]) - pd.Timestamp(u, unit="s", tz="UTC")).total_seconds())
        except ValueError:
            pass
    db.check("C08", "IMOS file-name hex time against header 'First Data' (logger clock), recorded only", True,
             f"header minus file-name time: median {np.median(offs):.1f} s, range {min(offs):.1f} to {max(offs):.1f} s (n={len(offs)}); the database uses the header time")

    # ------------------------------------------------------------------ digitised datasets
    D = os.path.join(MOD, "results-data/digitised")
    T0 = pd.Timestamp("2014-03-08", tz="UTC")

    def add_ds(**kw):
        base = dict(dataset_id=None, title=None, site_id=None, source_id=None, data_form=None, quantity=None, units=None,
                    context=None, t_start_utc=None, t_end_utc=None, time_basis=None, sample_rate_hz=None, resolution_note=None,
                    band_lo_hz=None, band_hi_hz=None, band_basis=None, continuity=None, n_segments=None, covered_s=None,
                    span_s=None, duty_fraction=None, path=None, registry_entry_id=None, status="CURRENT", caveat=None)
        base.update(kw)
        db.ins("dataset", base)

    def add_trace_dataset(ds, title, site, src, files, labels, ctx, units, quantity, band, band_basis, caveat, reg,
                          form="digitised_trace", res_note=None, extra_attrs=(), inside_axes_only=False):
        rows = []
        for i, (f, lab) in enumerate(zip(files, labels)):
            df, _ = read_csv_commented(f)
            if inside_axes_only and "outside_axes" in df.columns:
                df = df[df.outside_axes == 0]
            t = pd.to_datetime(df["utc"], utc=True, format="ISO8601", errors="coerce")
            parse_fail.append((ds, lab, int(t.isna().sum()), len(t)))
            t = t.dropna()
            t0, t1, n = t.min(), t.max(), len(t)
            dur = (t1 - t0).total_seconds()
            rows.append(dict(dataset_id=ds, seq=i, label=lab, t_start_utc=iso(t0), t_end_utc=iso(t1), duration_s=dur,
                             sample_rate_hz=round(n / dur, 2) if dur > 0 else None, n_samples=n,
                             band_lo_hz=band[0], band_hi_hz=band[1], role="figure panel", file_path="MOD:" + os.path.relpath(f, MOD),
                             bytes=os.path.getsize(f), sha256=sha256_file(f), sha256_check="computed at build"))
        t0 = min(r["t_start_utc"] for r in rows); t1 = max(r["t_end_utc"] for r in rows)
        cov, nwin = merged_cover([(r["t_start_utc"], r["t_end_utc"]) for r in rows], tol_s=2.0)
        span = (pd.Timestamp(t1) - pd.Timestamp(t0)).total_seconds()
        contiguous = nwin == 1
        add_ds(dataset_id=ds, title=title, site_id=site, source_id=src, data_form=form, quantity=quantity, units=units, context=ctx,
               t_start_utc=t0, t_end_utc=t1, time_basis="UTC as printed on the figure axis",
               sample_rate_hz=float(np.median([r["sample_rate_hz"] for r in rows if r["sample_rate_hz"]])),
               resolution_note=res_note, band_lo_hz=band[0], band_hi_hz=band[1], band_basis=band_basis,
               continuity="continuous" if contiguous else "separate windows", n_segments=len(rows), covered_s=cov, span_s=span,
               duty_fraction=cov / span if span else None, path=os.path.relpath(os.path.dirname(files[0]), MOD),
               registry_entry_id=reg, caveat=caveat)
        db.ins_many("segment", rows)
        for k, v in extra_attrs:
            db.attr("dataset", ds, k, v, source_id=src)
        return rows

    parse_fail = []
    KADRI_PROC = ("Kadri 2024 Methods: Butterworth IIR high-pass below 5 Hz (in addition to the CTBTO high-pass) and a 2-40 Hz "
                  "band-pass 'applied in general'. The Fig. 9 caption does not name the filter.")
    K9 = os.path.join(MOD, "data/kadri_fig9_digitised")
    add_trace_dataset("kadri2024_fig9_h01w", "Cape Leeuwin pressure trace, Kadri 2024 Fig. 9 panels a-c (digitised)", "H01W", "kadri2024",
                      [f"{K9}/kadri-2024-figure9-panel-{p}-H01W.csv" for p in "abc"], ["panel a", "panel b", "panel c"],
                      "MH370 7-8 Mar 2014", "Pa", "pressure (plotted trace)", (5.0, 40.0), "author processing (stated in Methods)",
                      "Envelope resolution only: PDF vector vertices of the plotted trace, about 14.5 vertices/s; not CTBTO samples. Element not stated.",
                      "in.module_data", res_note="PDF vector vertices of the plotted (decimated) waveform",
                      extra_attrs=[("author_processing", KADRI_PROC),
                                   ("digitisation_method", "PDF vector polylines of the plotted waveform (archive extraction, copied unchanged 22 Oct 2026)"),
                                   ("publication_page", "Fig. 9 a-c, p. 9")])
    add_trace_dataset("kadri2024_fig9_h08s", "Diego Garcia South pressure trace, Kadri 2024 Fig. 9 panels d-e (digitised)", "H08S", "kadri2024",
                      [f"{K9}/kadri-2024-figure9-panel-{p}-H08S.csv" for p in "de"], ["panel d", "panel e"],
                      "MH370 7-8 Mar 2014", "Pa", "pressure (plotted trace)", (5.0, 40.0), "author processing (stated in Methods)",
                      "Envelope resolution only (about 14.5 vertices/s). Panel e amplitude scale has a +8.8 dB step at the panel join: excluded from level work. Airgun shots throughout (shot table).",
                      "in.module_data", res_note="PDF vector vertices of the plotted (decimated) waveform",
                      extra_attrs=[("author_processing", KADRI_PROC),
                                   ("amplitude_caveat", "Panel e: +8.8 dB step at the panel join; amplitude scale unreliable."),
                                   ("publication_page", "Fig. 9 d-e, p. 9")])
    S1 = os.path.join(D, "kadri-2024/figS1-vector-traces")
    add_trace_dataset("kadri2024_figS1_h08s", "Diego Garcia South pressure trace, Kadri 2024 Fig. S1 panels a-c (digitised, first-route windows)", "H08S", "kadri2024_s1",
                      [f"{S1}/kadri-2024-figureS1-panel-{p}-H08S.csv" for p in "abc"], ["S1 panel a", "S1 panel b", "S1 panel c"],
                      "MH370 7-8 Mar 2014", "Pa", "pressure (plotted trace)", (5.0, 40.0), "author processing (stated in Methods)",
                      "PDF vector vertices, 41-82 vertices/s; spans use vertices inside the printed axes only.", "in.module_data",
                      res_note="PDF vector vertices", inside_axes_only=True, extra_attrs=[("author_processing", KADRI_PROC)])
    add_trace_dataset("kadri2024_figS1_h11s", "Wake Island South pressure trace, Kadri 2024 Fig. S1 panels d-e (digitised, first-route windows)", "H11S", "kadri2024_s1",
                      [f"{S1}/kadri-2024-figureS1-panel-{p}-H11S.csv" for p in "de"], ["S1 panel d", "S1 panel e"],
                      "MH370 7-8 Mar 2014", "Pa", "pressure (plotted trace)", (5.0, 40.0), "author processing (stated in Methods)",
                      "PDF vector vertices, about 44 vertices/s; spans use vertices inside the printed axes only.", "in.module_data",
                      res_note="PDF vector vertices", inside_axes_only=True, extra_attrs=[("author_processing", KADRI_PROC)])

    # Royer spectrogram panels, grouped per station
    RS = os.path.join(D, "royer-2016/spectrograms")
    panels = {}
    for f in sorted(glob.glob(f"{RS}/*.npz")):
        z = np.load(f, allow_pickle=True)
        stn = norm_station(str(z["station"]))
        panels.setdefault(stn, []).append((f, float(z["t_utc_s"].min()), float(z["t_utc_s"].max()), float(z["f_hz"].min()),
                                           float(z["f_hz"].max()), len(z["t_utc_s"])))
    for site, pl in panels.items():
        ds = f"royer2016_spectrograms_{site.lower()}"
        rows = []
        for i, (f, a0, a1, f0, f1, n) in enumerate(sorted(pl, key=lambda x: x[1])):
            rows.append(dict(dataset_id=ds, seq=i, label=os.path.basename(f).replace(".npz", ""),
                             t_start_utc=iso(T0 + pd.Timedelta(seconds=a0)), t_end_utc=iso(T0 + pd.Timedelta(seconds=a1)),
                             duration_s=a1 - a0, sample_rate_hz=round((n - 1) / (a1 - a0), 3), n_samples=n,
                             band_lo_hz=f0, band_hi_hz=f1, role="figure panel (dB grid)",
                             file_path="MOD:" + os.path.relpath(f, MOD), bytes=os.path.getsize(f), sha256=sha256_file(f),
                             sha256_check="computed at build"))
        iv = sorted((pd.Timestamp(r["t_start_utc"]), pd.Timestamp(r["t_end_utc"])) for r in rows)
        merged = []
        for s0, s1 in iv:
            if merged and s0 <= merged[-1][1] + pd.Timedelta(seconds=30):
                merged[-1][1] = max(merged[-1][1], s1)
            else:
                merged.append([s0, s1])
        cov = sum((b - c).total_seconds() for c, b in merged)
        span = (merged[-1][1] - merged[0][0]).total_seconds()
        tc = ("Cape Leeuwin figure times run 7.7-16.6 s later than Royer Table 5 picks (possible 16 s GPS-UTC handling); unresolved."
              if site == "H01W" else "OHASISBIO figure marks agree with Table 5 within 5 s.")
        add_ds(dataset_id=ds, title=f"{'Cape Leeuwin (element H01W2)' if site=='H01W' else site} spectrogram panels, Royer 2016 (digitised dB grids)",
               site_id=site, source_id="royer2016", data_form="digitised_spectrogram", quantity="power spectral density",
               units="dB re 1 uPa^2/Hz", context="MH370 7-8 Mar 2014", t_start_utc=iso(merged[0][0]), t_end_utc=iso(merged[-1][1]),
               time_basis="UTC as printed (tick-calibrated)",
               resolution_note="3-min panels 0.28 s/px x 0.32 Hz/px; 2-h appendix strips 1.56 s/px; Fig. 2 about 4 s/px; level +/-1.5 dB; colour scale 70-100 dB (clips above 100 dB)",
               band_lo_hz=min(r["band_lo_hz"] for r in rows), band_hi_hz=max(r["band_hi_hz"] for r in rows),
               band_basis="frequency axis of the published spectrogram",
               continuity="continuous" if len(merged) == 1 else "separate windows", n_segments=len(rows), covered_s=cov, span_s=span,
               duty_fraction=cov / span if span else None, path="results-data/digitised/royer-2016/spectrograms",
               registry_entry_id="in.royer_2016_digitised", caveat="Published figure, digitised; no waveform recordings from this hydrophone. " + tc)
        db.ins_many("segment", rows)
        db.attr("dataset", ds, "timing_caveat", tc, source_id="royer2016", evidence="module digitisation check (MANIFEST.csv)")
        db.attr("dataset", ds, "digitisation_method", "embedded JPX raster -> PNG; colour -> dB by nearest 'jet' colour; tick-calibrated time axis (prepare/digitise_royer_2016.py)", source_id="royer2016")

    # Royer events and picks
    ev = pd.read_csv(os.path.join(D, "royer-2016/royer_events.csv"))
    for _, r in ev.iterrows():
        db.ins("event", dict(event_id=f"royer{int(r['index'])}", source_id="royer2016", label=None if pd.isna(r.label) else r.label,
                             event_class=r.event_class, origin_utc=iso(pd.Timestamp(f"{r.origin_date} {r.origin_time_utc}", tz="UTC")),
                             lat=r.lat_deg, lon=r.lon_deg, err_lat_deg=r.err_lat_deg, err_lon_deg=r.err_lon_deg, err_time_s=r.err_time_s,
                             n_hydrophones=int(r.n_hydrophones), note=r.type_text))
    ar = pd.read_csv(os.path.join(D, "royer-2016/royer_arrivals.csv")).dropna(subset=["arrival_utc"])
    stmap = norm_station
    picks = []
    for _, r in ar.iterrows():
        picks.append(dict(dataset_id="royer2016_table5_picks", site_id=stmap(r.station), kind="published arrival pick",
                          label=f"{r.station} event {int(r['index'])}{'' if pd.isna(r.label) else ' (' + r.label + ')'}",
                          t_utc=iso(T0 + pd.Timedelta(seconds=float(r.arrival_s_after_T0))), t_end_utc=None, bearing_deg=None,
                          value=r.implied_speed_km_s, value_unit="implied speed km/s", event_id=f"royer{int(r['index'])}", note=None))
    tt = [p["t_utc"] for p in picks]
    add_ds(dataset_id="royer2016_table5_picks", title="Royer 2016 Table 5 picked arrival times (20 events, 10 hydrophones)",
           source_id="royer2016", data_form="digitised_picks", quantity="arrival time", units="UTC", context="MH370 7-8 Mar 2014",
           t_start_utc=min(tt), t_end_utc=max(tt), time_basis="UTC as printed (0.01 s)", continuity="point picks",
           path="results-data/digitised/royer-2016/royer_arrivals.csv", registry_entry_id="in.royer_2016_digitised",
           caveat="Implied path speed check: median 1.482 km/s, range 1.467-1.518 km/s. Cape Leeuwin picks run 7.7-16.6 s earlier than Royer's own figure marks.")
    fm = pd.read_csv(os.path.join(D, "royer-2016/royer_figure_marks.csv"))
    n0 = len(picks)
    for _, r in fm.iterrows():
        t1 = None if pd.isna(r.t_end_utc_s) else iso(T0 + pd.Timedelta(seconds=float(r.t_end_utc_s)))
        picks.append(dict(dataset_id="royer2016_figure_marks", site_id=stmap(r.station), kind=r.kind,
                          label=r.figure, t_utc=iso(T0 + pd.Timedelta(seconds=float(r.t_utc_s))), t_end_utc=t1, bearing_deg=None,
                          value=None if pd.isna(r.mark_minus_table5_s) else r.mark_minus_table5_s, value_unit="mark minus Table 5 (s)",
                          event_id=None, note=None if pd.isna(r.nearest_table5_label) else f"nearest Table 5 event {r.nearest_table5_label}"))
    tt = [p["t_utc"] for p in picks[n0:]]
    add_ds(dataset_id="royer2016_figure_marks", title="Royer 2016 author pick bars and arrows on Figs 4-8 and appendix strips (digitised)",
           source_id="royer2016", data_form="digitised_picks", quantity="arrival mark", units="UTC", context="MH370 7-8 Mar 2014",
           t_start_utc=min(tt), t_end_utc=max(tt), time_basis="UTC from tick-calibrated figure axis", continuity="point picks",
           path="results-data/digitised/royer-2016/royer_figure_marks.csv", registry_entry_id="in.royer_2016_digitised",
           caveat="+/-0.3 s (3-min panels), +/-1.6 s (strips). Cape Leeuwin marks 7.7-16.6 s later than Table 5.")

    k1 = pd.read_csv(f"{K9}/kadri-table1-transients.csv")
    n0 = len(picks)
    for _, r in k1.iterrows():
        picks.append(dict(dataset_id="kadri2024_table1", site_id="H01W", kind="published transient", label=r.event_id,
                          t_utc=iso(pd.Timestamp(f"2014-03-08 {r.time_utc}", tz="UTC")), bearing_deg=r.bearing_deg,
                          value=None, value_unit=None, event_id=None, note=r.source_status))
    tt = [p["t_utc"] for p in picks[n0:]]
    add_ds(dataset_id="kadri2024_table1", title="Kadri 2024 Table 1 transients at Cape Leeuwin (times and bearings)", site_id="H01W",
           source_id="kadri2024", data_form="digitised_table", quantity="transient time and bearing", units="UTC, deg",
           context="MH370 7-8 Mar 2014", t_start_utc=min(tt), t_end_utc=max(tt), time_basis="UTC as printed (1 s)", continuity="point picks",
           path="data/kadri_fig9_digitised/kadri-table1-transients.csv", registry_entry_id="in.module_data",
           caveat="Kadri's main signal carries two times: text 00:52:03 and caption 00:54:30 (both kept).")
    k19 = pd.read_csv(os.path.join(D, "kadri-2019/kadri2019_table3_ha08s_signals.csv"))
    n0 = len(picks)
    for _, r in k19.iterrows():
        hh, mi = map(int, r.time_utc.split(":"))
        t = {"HA_30": pd.Timestamp("2014-03-07 23:57", tz="UTC"), "HA_31": pd.Timestamp("2014-03-08 00:11", tz="UTC")}.get(
            r.signal, pd.Timestamp(f"2014-03-08 {hh:02d}:{mi:02d}", tz="UTC"))
        picks.append(dict(dataset_id="kadri2019_table3", site_id="H08S", kind="published signal", label=r.signal, t_utc=iso(t),
                          bearing_deg=r.bearing_from_HA08s_deg, value=None, value_unit=None, event_id=None, note=r.date_note))
    tt = [p["t_utc"] for p in picks[n0:]]
    add_ds(dataset_id="kadri2019_table3", title="Kadri 2019 Table 3 signals of interest at Diego Garcia South", site_id="H08S",
           source_id="kadri2019", data_form="digitised_table", quantity="signal time and bearing", units="UTC, deg",
           context="MH370 7-8 Mar 2014", t_start_utc=min(tt), t_end_utc=max(tt),
           time_basis="UTC as printed (1 min; two 12-hour readings converted per date_note)", continuity="point picks",
           path="results-data/digitised/kadri-2019/kadri2019_table3_ha08s_signals.csv", registry_entry_id="in.module_data",
           caveat="Times printed to the minute; HA_30 and HA_31 printed in 12-hour form.")
    for fig, site, desc, axis in [("fig5_ha01", "H01W", "CMST 2014 Fig. 5 automatic detections at Cape Leeuwin (times and bearings, digitised)", "00:00-08:00 UTC"),
                                  ("fig7_ha08s", "H08S", "CMST 2014 Fig. 7 automatic detections at Diego Garcia South (times and bearings, digitised)", "00:00-03:00 UTC")]:
        f = os.path.join(D, f"cmst-2014/cmst2014_{fig}_detections_DIGITISED.csv")
        df, _ = read_csv_commented(f)
        ds = f"cmst2014_{fig}_detections"
        t = pd.to_datetime(df.epoch_s, unit="s", utc=True)
        for _, r in df.iterrows():
            picks.append(dict(dataset_id=ds, site_id=site, kind=f"CMST detection (iteration {r.iteration})", label=None,
                              t_utc=iso(pd.Timestamp(r.epoch_s, unit="s", tz="UTC")), bearing_deg=r.bearing_deg, value=None,
                              value_unit=None, event_id=None, note=None if r.cross_confirmed == 1 else "one stroke only"))
        add_ds(dataset_id=ds, title=desc, site_id=site, source_id="cmst2014", data_form="digitised_picks", quantity="detection time and bearing",
               units="UTC, deg", context="MH370 7-8 Mar 2014", t_start_utc=iso(t.min()), t_end_utc=iso(t.max()),
               time_basis="hours after 00:00 UTC from the figure axis", continuity="point picks",
               resolution_note="axis reading +/-18 s, +/-0.3 deg", path=os.path.relpath(f, MOD), registry_entry_id="in.module_data",
               caveat=f"Detector output of CMST, digitised from the figure; not raw data. Figure time axis {axis}.")
    f = os.path.join(D, "cmst-2014/cmst2014_fig10_ha08s_tgs_detections_DIGITISED.csv")
    add_ds(dataset_id="cmst2014_fig10_tgs_detections", title="CMST 2014 Fig. 10 Diego Garcia South detections of the TGS seismic survey (digitised)",
           site_id="H08S", source_id="cmst2014", data_form="digitised_picks", quantity="detection time (axis seconds) and bearing",
           units="s (axis), deg", context="MH370 7-8 Mar 2014", time_basis="figure axis seconds; origin not printed in the caption",
           continuity="point picks", path=os.path.relpath(f, MOD), registry_entry_id="in.module_data",
           caveat="Time-axis origin is not printed in the caption: rows are in the imported table only, without UTC.")
    sh = pd.read_csv(os.path.join(MOD, "results-data/h08s_template/h08s_template_shots.csv"))
    for _, r in sh.iterrows():
        picks.append(dict(dataset_id="h08s_airgun_shots", site_id="H08S", kind="airgun shot", label=f"panel {r.panel}",
                          t_utc=iso(T0 + pd.Timedelta(seconds=float(r.t))), bearing_deg=None, value=r.rho, value_unit="template correlation",
                          event_id=None, note=None))
    add_ds(dataset_id="h08s_airgun_shots", title="Airgun shot times on the digitised Diego Garcia South panels (module shot table)",
           site_id="H08S", source_id="kadri2024", data_form="derived_from_digitised", quantity="shot arrival time", units="UTC",
           context="MH370 7-8 Mar 2014", t_start_utc=iso(T0 + pd.Timedelta(seconds=sh.t.min())), t_end_utc=iso(T0 + pd.Timedelta(seconds=sh.t.max())),
           time_basis="seconds after 00:00 UTC 8 Mar 2014 on the Kadri Fig. 9 d-e time axis", continuity="point picks",
           path="results-data/h08s_template/h08s_template_shots.csv", registry_entry_id="in.h08s_shots",
           caveat=f"Derived by the module from the digitised envelope; {len(sh)} shots, interval about 9.98 s. A coincident candidate is labelled, not excluded (Pete's rule).")
    db.ins_many("pick", picks)

    WR = os.path.join(D, "waveform-rasters")
    add_trace_dataset("cmst2014_fig1_imos3315", "Perth Canyon logger 3315 waveform envelope, CMST 2014 Fig. 1 (digitised raster)", "IMOS3315",
                      "cmst2014", [f"{WR}/cmst2014_fig1_perth_canyon_DIGITISED.csv"], ["Fig. 1 top"], "MH370 7-8 Mar 2014", "Pa",
                      "pressure envelope (upper/lower per pixel column)", (None, None), "not stated in the figure",
                      "Raster envelope (561x420 px): 0.69 s per pixel column. Contains the CMST event (peak 01:33:44).", "in.module_data",
                      res_note="0.69 s per pixel column")
    add_trace_dataset("cmst2014_fig2_h01w", "Cape Leeuwin 5-40 Hz band level of three elements, CMST 2014 Fig. 2 (digitised spectrogram)", "H01W",
                      "cmst2014", [f"{WR}/cmst2014_fig2_ha01_h{i}_band_DIGITISED.csv" for i in (1, 2, 3)], ["element 1", "element 2", "element 3"],
                      "MH370 7-8 Mar 2014", "dB re panel maximum", "5-40 Hz mean of the plotted spectrogram", (5.0, 40.0),
                      "band chosen at digitisation from a 0-125 Hz spectrogram", "Relative level only (dB re panel maximum).",
                      "in.module_data", form="digitised_band_series", res_note="0.69 s per pixel column; three elements over the same window")
    db.con.execute("UPDATE dataset SET continuity='continuous', covered_s=span_s, duty_fraction=1.0 WHERE dataset_id='cmst2014_fig2_h01w'")
    add_ds(dataset_id="kadri2017_figs_ha01", title="Kadri 2017 figure rasters, including Cape Leeuwin 19:00-20:00 UTC 7 Mar 2014 entropy/bearing (Fig. 8)",
           site_id="H01W", source_id="kadri2017", data_form="raster_copy", quantity="figure image", context="MH370 7-8 Mar 2014",
           t_start_utc="2014-03-07T19:00:00.000Z", t_end_utc="2014-03-07T20:00:00.000Z", time_basis="figure axis as printed",
           band_lo_hz=5.0, band_basis="Kadri 2017 chain: 5 Hz high-pass + entropy (4 s window)",
           continuity="continuous", n_segments=1, path="results-data/digitised/ground-truth-cases/figures/",
           registry_entry_id="in.module_data", caveat="Raster images only; waveforms not traced.")

    # ------------------------------------------------------------------ calibration-case datasets (other stations / years)
    for ds, title, site, src, ctx, names in [
        ("kadri2024_fig5a_af447_h10s", "AF447 (1 Jun 2009) at Ascension South, Kadri 2024 Fig. 5a (digitised raster)", "H10S", "kadri2024", "calibration: AF447 2009", ["kadri2024_fig5a_af447_H10S"]),
        ("kadri2024_fig7_sanjuan", "ARA San Juan (15 Nov 2017), Kadri 2024 Fig. 7 (digitised raster)", None, "kadri2024", "calibration: ARA San Juan 2017", ["kadri2024_fig7_sanjuan_H03S", "kadri2024_fig7_sanjuan_H04S", "kadri2024_fig7_sanjuan_H10N"]),
        ("kadri2024_fig8_grenade", "Depth charge (1 Dec 2017), Kadri 2024 Fig. 8 (digitised raster)", None, "kadri2024", "calibration: depth charge 2017", ["kadri2024_fig8_grenade_H03S", "kadri2024_fig8_grenade_H04S", "kadri2024_fig8_grenade_H10N"])]:
        add_trace_dataset(ds, title, site, src, [f"{WR}/{n}_DIGITISED.csv" for n in names], [n.split("_")[-1] for n in names], ctx, "Pa",
                          "pressure envelope", (5.0, 40.0), "author processing (stated in Methods)", "Raster envelope of the published JPEG (~750 px wide).",
                          "in.module_data", res_note="raster envelope")
    nf = sorted(glob.glob(f"{WR}/nielsen2021_fig3_*_DIGITISED.csv"))
    for case, ctx in [("sanjuan", "calibration: ARA San Juan 2017"), ("charge", "calibration: depth charge 2017")]:
        files = [f for f in nf if f"_{case}_" in f]
        add_trace_dataset(f"nielsen2021_fig3_{case}", f"Nielsen 2021 Fig. 3 normalised traces, {case} (digitised raster)", None, "nielsen2021",
                          files, [os.path.basename(f).split(f"{case}_")[1].replace("_DIGITISED.csv", "") for f in files], ctx,
                          "normalised", "pressure envelope", (None, None), "not stated", "Normalised amplitude only.", "in.module_data",
                          res_note="raster envelope")
    vf = sorted(glob.glob(f"{WR}/vergoz2021_fig2_*_DIGITISED.csv"))
    add_trace_dataset("vergoz2021_fig2", "Vergoz 2021 Fig. 2 normalised traces (digitised raster)", None, "vergoz2021", vf,
                      [os.path.basename(f).replace("vergoz2021_fig2_", "").replace("_DIGITISED.csv", "") for f in vf],
                      "calibration: ARA San Juan / depth charge 2017", "normalised", "pressure envelope", (None, None), "not stated",
                      "Normalised amplitude only.", "in.module_data", res_note="raster envelope")
    mz, _ = read_csv_commented(os.path.join(D, "metz2023/fig3CD_rms_envelopes_0p05s_DIGITISED.csv"))
    MD = pd.Timestamp("2019-04-09", tz="UTC")
    add_ds(dataset_id="metz2023_fig3cd_h11", title="F-35A crash (9 Apr 2019) arrival at Wake Island North and South, Metz 2023 Fig. 3C-D 1 s RMS (digitised)",
           site_id="H11N", source_id="metz2023", data_form="digitised_band_series", quantity="1 s RMS level", units="dB re 1 uPa",
           context="calibration: F-35A 2019", t_start_utc=iso(MD + pd.Timedelta(seconds=float(mz.utc_s_of_day.min()))),
           t_end_utc=iso(MD + pd.Timedelta(seconds=float(mz.utc_s_of_day.max()))), time_basis="UTC as printed",
           sample_rate_hz=20.0, resolution_note="resampled to 0.05 s; tick residuals < 0.01 s / 0.004 dB", band_lo_hz=4.0, band_hi_hz=64.0,
           band_basis="author processing (4-64 Hz)", continuity="separate windows", path="results-data/digitised/metz2023/",
           registry_entry_id="in.module_data", caveat="Elements H11N1-3 and H11S1-3; two 30 s windows. Date from the published case (9 Apr 2019); the paper text gives times of day.")
    add_ds(dataset_id="brown2026_figC10_h08s", title="Fireball 7 Oct 2004 at Diego Garcia South, Brown 2026 Fig. C.10 envelopes (digitised)",
           site_id="H08S", source_id="brown2026", data_form="digitised_trace", quantity="pixel envelope (relative)", units="px",
           context="calibration: fireball 2004", t_start_utc="2004-10-07T13:30:00.000Z", t_end_utc="2004-10-07T14:30:00.000Z",
           time_basis="UTC as printed", resolution_note="2.16 s per px; no amplitude axis", band_basis="unfiltered (caption)",
           continuity="continuous", path="results-data/digitised/brown-2026/", registry_entry_id="in.module_data", caveat="Relative level only.")
    add_ds(dataset_id="brown2026_fig7_h03n", title="Fireball 2 Sep 2003 at Juan Fernandez North, Brown 2026 Fig. 7 (digitised)",
           site_id="H03N", source_id="brown2026", data_form="digitised_trace", quantity="waveform envelope and spectrum", units="counts",
           context="calibration: fireball 2003", band_lo_hz=4.0, band_hi_hz=9.0, band_basis="best beam 4-9 Hz (caption)",
           continuity="continuous", path="results-data/digitised/brown-2026/", registry_entry_id="in.module_data",
           caveat="Amplitude in uncalibrated counts.")
    add_ds(dataset_id="blackman2004_fig23_tl", title="2001 airgun transmission loss to Cape Leeuwin and Diego Garcia, Blackman 2004 Fig. 23 (digitised)",
           source_id="blackman2004", data_form="digitised_table", quantity="observed transmission loss against frequency",
           units="dB, Hz", context="calibration: airgun shots 2001", time_basis="no time axis (median over shots)",
           resolution_note="0.35 Hz, 0.28 dB per px; reading +/-1 to +/-2 dB", continuity="no time axis",
           path="results-data/digitised/blackman-2004/", registry_entry_id="in.module_data",
           caveat="Panels CL (H01W: air7, air9), DGN (H08N: air1-5), DGS (H08S: air7-9). Only air9 used for validation (RMS 7.9 dB).")
    add_ds(dataset_id="blackman_tables", title="Blackman 2001/2003 calibration tables: shot lines, events, receiver observations, transmission loss",
           source_id="blackman2004", data_form="digitised_table", quantity="calibration-source tables", context="calibration: airgun shots 2001 and 2003 sources",
           time_basis="as printed", continuity="no time axis", path="data/blackman/", registry_entry_id="in.module_data")
    add_ds(dataset_id="ground_truth_tables", title="Ground-truth case tables (Kadri 2017, Nielsen 2021, Vergoz 2021)",
           data_form="digitised_table", quantity="event locations, times, reflectors, delays", context="calibration: ground-truth cases",
           continuity="no time axis", path="results-data/digitised/ground-truth-cases/", registry_entry_id="in.module_data")
    add_ds(dataset_id="duncan2023_fig3", title="Duncan & Dall'Osto 2023 Fig. 3 modelled relative signal strength and depth along paths from Cape Leeuwin (digitised)",
           site_id="H01W", source_id="duncan2023", data_form="digitised_table", quantity="modelled relative level against range", units="dB, km",
           context="calibration: model comparison", continuity="no time axis", path="data/", registry_entry_id="in.module_data",
           caveat="Model output, not a measurement.")
    add_ds(dataset_id="kadri2024_published_figures", title="Kadri 2024 published figure images (Europe PMC JPEGs)", source_id="kadri2024",
           data_form="raster_copy", quantity="figure images", context="MH370 7-8 Mar 2014 and calibration cases", continuity="no time axis",
           path="results-data/digitised/kadri-2024/published-figures-pmc/", registry_entry_id="in.module_data", caveat="About 750 px wide.")
    add_ds(dataset_id="royer2016_figures", title="Royer 2016 figure rasters, calibration files and overlays", source_id="royer2016",
           data_form="raster_copy", quantity="figure images and calibration json", context="MH370 7-8 Mar 2014", continuity="no time axis",
           path="results-data/digitised/royer-2016/figures/", registry_entry_id="in.royer_2016_digitised")
    add_ds(dataset_id="cmst2014_figures", title="CMST 2014 figure rasters and overlays", source_id="cmst2014",
           data_form="raster_copy", quantity="figure images", context="MH370 7-8 Mar 2014", continuity="no time axis",
           path="results-data/digitised/cmst-2014/figures/", registry_entry_id="in.module_data")
    add_ds(dataset_id="metz2023_other", title="Metz 2023 other digitised panels (spectrograms, detection windows, sound speed, local stations)",
           source_id="metz2023", data_form="digitised_table", quantity="spectrogram grids, detection windows, sound-speed profiles",
           context="calibration: F-35A 2019", continuity="no time axis", path="results-data/digitised/metz2023/", registry_entry_id="in.module_data")
    add_ds(dataset_id="brown2026_other", title="Brown 2026 other digitised items (Arons relation, Fig. C.12, rasters)", source_id="brown2026",
           data_form="digitised_table", quantity="relation, envelopes, spectrograms", context="calibration: fireballs 2003-2004",
           continuity="no time axis", path="results-data/digitised/brown-2026/", registry_entry_id="in.module_data")
    add_ds(dataset_id="kadri2019_other", title="Kadri 2019 route tables and figure rasters", source_id="kadri2019",
           data_form="digitised_table", quantity="route alternatives, figures", context="MH370 7-8 Mar 2014", continuity="no time axis",
           path="results-data/digitised/kadri-2019/", registry_entry_id="in.module_data")
    add_ds(dataset_id="digitisation_qc_files", title="Digitisation check images (overlays) and waveform-raster summary table",
           data_form="raster_copy", quantity="check images, summary", context="all", continuity="no time axis",
           path="results-data/digitised/waveform-rasters/", registry_entry_id="in.module_data")
    add_ds(dataset_id="module_reference_files", title="Module reference files: station list, IMOS recordings index, pre-registration, background manifest, IMS responses, calibration gain",
           data_form="instrument_metadata", quantity="reference tables", context="all", continuity="no time axis", path="data/",
           registry_entry_id="in.module_data")

    # ------------------------------------------------------------------ verbatim import of every digitised/module data CSV + file references
    def link(rel):
        rules = [
            ("data/kadri_fig9_digitised/kadri-table1", "kadri2024_table1"), ("data/kadri_fig9_digitised/kadri-2024-figure9-panel-a", "kadri2024_fig9_h01w"),
            ("data/kadri_fig9_digitised/kadri-2024-figure9-panel-b", "kadri2024_fig9_h01w"), ("data/kadri_fig9_digitised/kadri-2024-figure9-panel-c", "kadri2024_fig9_h01w"),
            ("data/kadri_fig9_digitised/kadri-2024-figure9-panel-d", "kadri2024_fig9_h08s"), ("data/kadri_fig9_digitised/kadri-2024-figure9-panel-e", "kadri2024_fig9_h08s"),
            ("data/kadri_fig9_digitised", "kadri2024_fig9_h01w"),
            ("results-data/digitised/kadri-2024/figS1-vector-traces/kadri-2024-figureS1-panel-d", "kadri2024_figS1_h11s"),
            ("results-data/digitised/kadri-2024/figS1-vector-traces/kadri-2024-figureS1-panel-e", "kadri2024_figS1_h11s"),
            ("results-data/digitised/kadri-2024/figS1", "kadri2024_figS1_h08s"), ("results-data/digitised/kadri-2024/published", "kadri2024_published_figures"),
            ("results-data/digitised/royer-2016/royer_arrivals", "royer2016_table5_picks"), ("results-data/digitised/royer-2016/royer_figure_marks", "royer2016_figure_marks"),
            ("results-data/digitised/royer-2016/spectrograms", "SPEC"), ("results-data/digitised/royer-2016", "royer2016_figures"),
            ("results-data/digitised/cmst-2014/cmst2014_fig5", "cmst2014_fig5_ha01_detections"), ("results-data/digitised/cmst-2014/cmst2014_fig7_ha08s", "cmst2014_fig7_ha08s_detections"),
            ("results-data/digitised/cmst-2014/cmst2014_fig10_ha08s", "cmst2014_fig10_tgs_detections"), ("results-data/digitised/cmst-2014", "cmst2014_figures"),
            ("results-data/digitised/waveform-rasters/cmst2014_fig1", "cmst2014_fig1_imos3315"), ("results-data/digitised/waveform-rasters/cmst_fig1", "cmst2014_fig1_imos3315"),
            ("results-data/digitised/waveform-rasters/imos3315", "cmst2014_fig1_imos3315"), ("results-data/digitised/waveform-rasters/cmst2014_fig2", "cmst2014_fig2_h01w"),
            ("results-data/digitised/waveform-rasters/kadri2024_fig5a", "kadri2024_fig5a_af447_h10s"), ("results-data/digitised/waveform-rasters/kadri2024_fig7", "kadri2024_fig7_sanjuan"),
            ("results-data/digitised/waveform-rasters/kadri2024_fig8", "kadri2024_fig8_grenade"), ("results-data/digitised/waveform-rasters/nielsen2021_fig3_sanjuan", "nielsen2021_fig3_sanjuan"),
            ("results-data/digitised/waveform-rasters/nielsen2021_fig3_charge", "nielsen2021_fig3_charge"), ("results-data/digitised/waveform-rasters/vergoz", "vergoz2021_fig2"),
            ("results-data/digitised/metz2023/fig3CD", "metz2023_fig3cd_h11"), ("results-data/digitised/metz2023", "metz2023_other"),
            ("results-data/digitised/brown-2026/figC10", "brown2026_figC10_h08s"), ("results-data/digitised/brown-2026/fig7", "brown2026_fig7_h03n"),
            ("results-data/digitised/brown-2026", "brown2026_other"),
            ("results-data/digitised/ground-truth-cases/figures/kadri2017", "kadri2017_figs_ha01"), ("results-data/digitised/kadri-2017", "kadri2017_figs_ha01"),
            ("results-data/digitised/waveform-rasters/overlays", "digitisation_qc_files"), ("results-data/digitised/waveform-rasters/waveform_raster_summary", "digitisation_qc_files"), ("results-data/digitised/blackman-2004", "blackman2004_fig23_tl"),
            ("data/blackman", "blackman_tables"), ("results-data/digitised/ground-truth-cases", "ground_truth_tables"),
            ("results-data/digitised/kadri-2019/kadri2019_table3", "kadri2019_table3"), ("results-data/digitised/kadri-2019", "kadri2019_other"),
            ("data/duncan", "duncan2023_fig3"), ("results-data/h08s_template/h08s_template_shots", "h08s_airgun_shots"),
            ("data/", "module_reference_files"), ("results-data/imos1d/calibration_gain", "module_reference_files"),
            ("results-data/digitised/MANIFEST", "module_reference_files"),
        ]
        d = next((d for p, d in rules if rel.startswith(p)), None)
        if d == "SPEC":
            stn = re.search(r"_(h01w2|sseir|swams\d|mad|wker|ncro)_", os.path.basename(rel))
            d = f"royer2016_spectrograms_{('h01w' if stn.group(1) == 'h01w2' else stn.group(1))}" if stn else "royer2016_figures"
        return d

    csvs = sorted(set(glob.glob(f"{MOD}/data/**/*.csv", recursive=True) + glob.glob(f"{D}/**/*.csv", recursive=True)
                      + [os.path.join(MOD, "results-data/h08s_template/h08s_template_shots.csv"),
                         os.path.join(MOD, "results-data/imos1d/calibration_gain.csv")]))
    csvs = [c for c in csvs if "/stub/" not in c and "/kadri_package/" not in c and "/ocean_paths/" not in c]
    used, n_imp, unlinked = set(), 0, []
    for c in csvs:
        rel = os.path.relpath(c, MOD)
        dsid = link(rel)
        if dsid is None:
            unlinked.append(rel)
        name = ("dg_" + re.sub(r"[^a-z0-9]+", "_", rel.lower().replace("results-data/digitised/", "").replace(".csv", "")).strip("_"))[:120]
        base, k = name, 2
        while name in used:
            name = f"{base}_{k}"; k += 1
        used.add(name)
        df, com = read_csv_commented(c)
        df.columns = [str(x) if str(x).strip() and not str(x).startswith("Unnamed") else f"col{i}" for i, x in enumerate(df.columns)]
        df.to_sql(name, db.con, index=False)
        db.ins("imported_table", dict(table_name=name, source_file="MOD:" + rel, sha256=sha256_file(c), n_rows=len(df), n_cols=df.shape[1],
                                      header_comment=com or None, dataset_id=dsid))
        n_imp += 1
    n_ref = 0
    for f in sorted(set(glob.glob(f"{D}/**/*", recursive=True) + glob.glob(f"{MOD}/data/**/*", recursive=True))):
        if os.path.isdir(f) or f.endswith(".csv") or "/stub/" in f or "/kadri_package/" in f or "/ocean_paths/" in f:
            continue
        rel = os.path.relpath(f, MOD)
        dsid = link(rel)
        if dsid is None:
            unlinked.append(rel)
        db.ins("file_ref", dict(file_path="MOD:" + rel, dataset_id=dsid, kind=os.path.splitext(f)[1].lstrip(".").lower(),
                                bytes=os.path.getsize(f), sha256=sha256_file(f), note=None))
        n_ref += 1
    db.check("C09", "Digitised and module data files: CSV imported verbatim as tables, other files referenced with SHA-256", True,
             f"{n_imp} tables imported; {n_ref} non-CSV files referenced. Excluded by design: data/stub (test stubs), data/kadri_package and data/ocean_paths (derived products)")
    db.check("C14", "Every imported table and file reference is linked to a dataset", not unlinked, f"{len(unlinked)} unlinked: {unlinked[:20]}")

    # ------------------------------------------------------------------ integrity checks
    con = db.con
    q = lambda s: con.execute(s).fetchone()[0]
    db.check("C10", "Every dataset site_id exists in site", q("SELECT COUNT(*) FROM dataset WHERE site_id IS NOT NULL AND site_id NOT IN (SELECT site_id FROM site)") == 0, "orphan count checked")
    bp = [r[0] for r in con.execute("SELECT DISTINCT site_id FROM pick WHERE site_id IS NOT NULL AND site_id NOT IN (SELECT site_id FROM site)")]
    db.check("C11", "Every pick site_id exists in site", not bp, f"orphans: {bp}")
    db.check("C12", "Segment end not before start", q("SELECT COUNT(*) FROM segment WHERE t_end_utc < t_start_utc") == 0, "checked")
    reg_ids = {e["id"] for e in json.load(open(os.path.join(MOD, "registry/REGISTRY.json")))["entries"]}
    br = [r[0] for r in con.execute("SELECT DISTINCT registry_entry_id FROM dataset WHERE registry_entry_id IS NOT NULL")]
    missing = [b for b in br if b not in reg_ids]
    db.check("C13", "Every dataset registry_entry_id exists in REGISTRY.json", not missing, f"{len(br)} ids used; missing: {missing}")
    for cid, (pd_, sd_) in {"C15": ("kadri2024_table1", "kadri2024_fig9_h01w"), "C16": ("h08s_airgun_shots", "kadri2024_fig9_h08s")}.items():
        ins = q(f"""SELECT COUNT(*) FROM pick p WHERE p.dataset_id='{pd_}' AND EXISTS (SELECT 1 FROM segment s WHERE s.dataset_id='{sd_}'
                    AND p.t_utc BETWEEN s.t_start_utc AND s.t_end_utc)""")
        tot = q(f"SELECT COUNT(*) FROM pick WHERE dataset_id='{pd_}'")
        db.check(cid, f"{pd_} times lie inside the {sd_} panels", ins == tot, f"{ins} of {tot}")
    nds = q("SELECT COUNT(*) FROM dataset WHERE dataset_id NOT IN (SELECT DISTINCT dataset_id FROM segment) AND dataset_id NOT IN (SELECT DISTINCT dataset_id FROM pick) AND dataset_id NOT IN (SELECT DISTINCT dataset_id FROM imported_table WHERE dataset_id IS NOT NULL) AND dataset_id NOT IN (SELECT DISTINCT dataset_id FROM file_ref WHERE dataset_id IS NOT NULL)")
    db.check("C18", "Every dataset has at least one segment, pick, imported table or file reference", nds == 0, f"{nds} empty datasets")

    bad = [p for p in parse_fail if p[2]]
    db.check("C19", "Digitised traces: every UTC value parses (ISO 8601)", not bad, f"{len(parse_fail)} files; failures: {bad}")
    dup = con.execute("""SELECT a.dataset_id, b.dataset_id, COUNT(*), MIN(a.t_start_utc), MAX(a.t_start_utc) FROM segment a JOIN segment b
                         ON a.sha256 = b.sha256 AND a.dataset_id < b.dataset_id GROUP BY a.dataset_id, b.dataset_id""").fetchall()
    for da, dbb, n, t0, t1 in dup:
        con.execute("UPDATE segment SET same_file_in=? WHERE dataset_id=? AND sha256 IN (SELECT sha256 FROM segment WHERE dataset_id=?)", (dbb, da, dbb))
        con.execute("UPDATE segment SET same_file_in=? WHERE dataset_id=? AND sha256 IN (SELECT sha256 FROM segment WHERE dataset_id=?)", (da, dbb, da))
    db.check("C20", "Records held in two IMOS sets (byte-identical files; marked in segment.same_file_in, counted once for coverage)", True,
             "; ".join(f"{n} records in both {da} and {dbb} ({t0[:16]} to {t1[:16]})" for da, dbb, n, t0, t1 in dup) or "none")
    con.executescript(VIEWS)
    for k, v in dict(schema_version=SCHEMA_VERSION, built_utc=BUILD_UTC, module_git_head=a.git_head,
                     module_root="MOD = Claude Science Project Sep 29/engine/hypotheses/hydroacoustics (branch hypothesis/hydroacoustics)",
                     inputs_root="INPUTS = ~/Downloads/mh370-inputs/hydroacoustics",
                     scope="Data only: raw recordings and digitised published data. Derived results stay in registry/REGISTRY.json.",
                     time_convention="All *_utc columns are ISO 8601 UTC strings. IMOS: true UTC = logger - e(t) (convention A).",
                     extend="New property: declare it in attribute_key, then add attribute rows. New data: dataset row plus segment/pick rows; re-run checks.").items():
        db.ins("meta", dict(key=k, value=v))
    con.commit()
    con.execute("VACUUM")
    con.close()
    for c in db.checks:
        print(("PASS " if c[2] else "FAIL ") + c[0], "|", c[1], "|", c[3][:220])


if __name__ == "__main__":
    main()
