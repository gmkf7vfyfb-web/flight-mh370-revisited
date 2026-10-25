#!/usr/bin/env python3
"""
build_noise_coupling.py - stage 2 of hydro_data.sqlite: background noise and acoustic coupling in the same database.

Run after build_hydro_data_db.py (stage 1). It (re)creates only the tables listed in NEW_TABLES and NEW_VIEWS, so it can
be re-run on its own. Data only: values as measured, traced, digitised or published, each with its definition, unit,
source file, SHA-256 and registry entry. Analysis results stay in the registry.

Inputs
  --db        hydro_data.sqlite (stage 1 already built)
  --mod       hydroacoustics module root (branch hypothesis/hydroacoustics); reads results-data/{imos1d, blackman_noise,
              kadri_fig9_noise, metz_f35a, f35a_cal} and registry/REGISTRY.json
  --coupling  folder with the coupling inputs and MANIFEST.tsv (file, artifact_version, producer, sha256, role);
              written by the coupling thread (session c764a583); this script never edits them
  --record    output path for the generated record (markdown), NOISE_COUPLING_RECORD.md

Rules built in (checks K.. and N..):
  * Every noise value has one quantity from quantity_def (unit fixed by the quantity) and keeps its original value/unit.
  * Every coupling value has a definition (coupling_definition) and the propagation relation it must be used with.
    The module-chain view never returns a path-blind (Arons-equivalent) value and the path-blind view never returns a
    model-inverted value. Implosion values have their own denominator (P V) and are kept out of both impact views.
  * The F-35A values are points on one (coupling, source depth, spectrum) curve from one recording. No ruling is needed
    (Pete, 24 Oct 2026: "The F35 ruling was a red herring").
  * Text that limits or discounts a source ("not held", "closed", "paywalled", "no legitimate copy") is listed for Pete
    in check K09 (standing rule on labels, 22 Oct 2026); it is not used to exclude anything.
"""
import argparse, hashlib, json, re, sqlite3, textwrap
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STAGE = "noise-coupling v1"
THIRD_OCT = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
RESTRICTIVE = ["not held", "closed access", "(closed)", "paywalled", "paywall", "unobtainable", "no legitimate copy", "unusable", "restricted"]
PETE_F35 = "One point on the F-35A (coupling, source depth, spectrum) curve from one recording; no ruling needed (Pete, 24 Oct 2026: 'The F35 ruling was a red herring')."

NEW_TABLES = ["quantity_def", "noise_estimate", "noise_condition", "coupling_definition", "coupling_value",
              "coupling_evidence", "coupling_curve", "cp_impact_source_parameters", "stage2_input"]
NEW_VIEWS = ["v_noise_summary", "v_noise_8mar2014", "v_coupling_for_module_chain", "v_coupling_path_blind", "v_coupling_implosion"]

SCHEMA = """
CREATE TABLE quantity_def (quantity_id TEXT PRIMARY KEY, name TEXT NOT NULL, unit TEXT NOT NULL, definition TEXT NOT NULL);
CREATE TABLE stage2_input (file_path TEXT PRIMARY KEY, kind TEXT, sha256 TEXT, bytes INTEGER, producer TEXT, artifact_version TEXT,
  registry_entry_id TEXT, registry_status TEXT, note TEXT);
CREATE TABLE noise_estimate (
  noise_id INTEGER PRIMARY KEY, site_id TEXT REFERENCES site(site_id), sensor_or_element TEXT,
  context TEXT NOT NULL,                 -- 'MH370 8 Mar 2014' | 'IMS 2003 Blackman cruise' | 'calibration: F-35A 9 Apr 2019'
  period_start_utc TEXT, period_end_utc TEXT, period_note TEXT,
  band_lo_hz REAL NOT NULL, band_hi_hz REAL NOT NULL, band_label TEXT,
  quantity_id TEXT NOT NULL REFERENCES quantity_def(quantity_id),
  statistic TEXT NOT NULL,               -- p5 | p10 | median | p90 | p95 | mean | value | p99_minus_median
  value REAL NOT NULL, unit TEXT NOT NULL, original_value REAL, original_unit TEXT, original_field TEXT,
  averaging TEXT, n_items INTEGER, method TEXT NOT NULL, source_id TEXT REFERENCES source(source_id),
  dataset_id TEXT, segment_file TEXT, input_file TEXT NOT NULL, input_sha256 TEXT NOT NULL,
  registry_entry_id TEXT, registry_status TEXT, role TEXT, caveat TEXT);
CREATE TABLE noise_condition (
  site_id TEXT, context TEXT, condition TEXT NOT NULL, effect TEXT, source TEXT, input_file TEXT);
CREATE TABLE coupling_definition (
  def_id TEXT PRIMARY KEY, name TEXT NOT NULL, numerator TEXT, denominator TEXT, propagation_relation TEXT NOT NULL,
  allowed_chain TEXT NOT NULL,           -- module_tl | path_blind | near_field_source_model | implosion_branch
  rule TEXT NOT NULL);
CREATE TABLE coupling_value (
  value_id TEXT PRIMARY KEY, def_id TEXT NOT NULL REFERENCES coupling_definition(def_id), definition_as_written TEXT,
  value_as_written TEXT, value_num REAL, range_low REAL, range_high REAL,
  numerator TEXT, denominator TEXT, band_hz TEXT, source_depth_m TEXT, mechanism_and_scale TEXT,
  propagation_relation_required TEXT, reference TEXT, read_in_primary_as_written TEXT,
  role_in_prior TEXT, role_status TEXT NOT NULL, evidence_id TEXT, f35a_note TEXT, notes TEXT, input_file TEXT, input_sha256 TEXT);
CREATE TABLE coupling_evidence (
  evidence_id TEXT PRIMARY KEY, evidence TEXT, what_it_measures TEXT, observation_operator TEXT, what_it_constrains TEXT,
  regime TEXT, how_it_is_used TEXT, independence_group TEXT NOT NULL, main_error_terms TEXT, source TEXT,
  input_file TEXT, input_sha256 TEXT);
CREATE TABLE coupling_curve (
  curve_row INTEGER PRIMARY KEY, curve_id TEXT NOT NULL, evidence_id TEXT, def_id TEXT REFERENCES coupling_definition(def_id),
  station TEXT, path_or_point TEXT, bottom TEXT, src_depth_m REAL, tl_model TEXT, tau_s REAL, spectral_slope REAL,
  energy_case TEXT, noise_def TEXT, template TEXT, eta REAL NOT NULL, definition_as_written TEXT,
  input_file TEXT, registry_entry_id TEXT, registry_status TEXT, status_note TEXT);
"""
VIEWS = """
CREATE VIEW v_noise_summary AS
SELECT n.site_id, s.name AS site_name, n.context, n.band_label, n.band_lo_hz, n.band_hi_hz, q.name AS quantity, n.statistic,
       round(n.value, 2) AS value, n.unit, n.averaging, n.n_items, n.method, n.role, n.registry_entry_id, n.registry_status, n.caveat
FROM noise_estimate n LEFT JOIN site s USING(site_id) JOIN quantity_def q USING(quantity_id)
WHERE n.statistic != 'value';
CREATE VIEW v_noise_8mar2014 AS
SELECT * FROM v_noise_summary WHERE context = 'MH370 8 Mar 2014';
CREATE VIEW v_coupling_for_module_chain AS
SELECT v.value_id AS item, 'value' AS kind, v.def_id, v.value_num, v.range_low, v.range_high, v.source_depth_m, v.role_in_prior, v.role_status, v.f35a_note
FROM coupling_value v JOIN coupling_definition d USING(def_id)
WHERE d.allowed_chain = 'module_tl' AND v.role_status NOT IN ('EXCLUDED', 'SUPERSEDED')
UNION ALL
SELECT c.curve_id || ' z=' || c.src_depth_m || ' m', 'curve', c.def_id, NULL, min(c.eta), max(c.eta), c.src_depth_m, NULL, c.status_note, NULL
FROM coupling_curve c JOIN coupling_definition d USING(def_id) JOIN coupling_evidence e ON e.evidence_id = c.evidence_id
WHERE d.allowed_chain = 'module_tl' AND c.status_note NOT LIKE 'SUPERSEDED%' AND e.how_it_is_used LIKE 'LIKELIHOOD TERM%'
GROUP BY c.curve_id, c.src_depth_m;
CREATE VIEW v_coupling_path_blind AS
SELECT v.value_id, v.def_id, v.value_num, v.range_low, v.range_high, v.role_in_prior, v.role_status, v.f35a_note, v.notes
FROM coupling_value v JOIN coupling_definition d USING(def_id) WHERE d.allowed_chain = 'path_blind';
CREATE VIEW v_coupling_implosion AS
SELECT v.value_id, v.def_id, v.value_num, v.range_low, v.range_high, v.denominator, v.role_in_prior, v.role_status
FROM coupling_value v JOIN coupling_definition d USING(def_id) WHERE d.allowed_chain = 'implosion_branch';
"""
QUANTITIES = [
    ("band_mean_psd", "band-averaged noise power spectral density", "dB re 1 uPa^2/Hz",
     "10 log10 of the mean of the linear PSD over the band; Welch or periodogram estimate as stated in 'averaging'."),
    ("rms_level", "RMS sound pressure level in a band", "dB re 1 uPa",
     "20 log10 of the RMS pressure over the stated averaging window and band."),
    ("level_spread", "level difference", "dB", "Difference between two statistics of the same level series (for example p99 minus median)."),
]
DEFINITIONS = [
    ("D1", "source radiated acoustic energy / impact kinetic energy (model-inverted)",
     "total acoustic energy radiated at the source (stated spectral model and normalisation band)", "impact kinetic energy 0.5 m v^2",
     "explicit source depth (surface image) + module transmission loss (KRAKEN, RAM correction) on each bathymetric path, receiver depth, instrument response",
     "module_tl", "Use only with the module propagation chain and the source depth and spectrum it was inverted with. Never with the Arons relation."),
    ("D2", "Arons-equivalent in-channel TNT energy / impact kinetic energy (path-blind)",
     "4.184e6 J/kg x W, W from Arons (1954) for the observed peak pressure", "impact kinetic energy",
     "Arons 1954 peak-pressure law at the source-receiver range; site and path effects are inside the value",
     "path_blind", "Use only as an end-to-end screen with the Arons relation. Never combine with a transmission-loss model (path counted twice)."),
    ("D3", "near-field measured acoustic energy / kinetic or hammer energy",
     "acoustic energy measured near the source (tank, near-field array)", "kinetic (or hammer) energy",
     "near-field / free-field measurement; needs an explicit source model (spectrum, depth, directivity) and full transmission loss",
     "near_field_source_model", "Envelope and scaling evidence only. Not coupling into the deep sound channel."),
    ("D4", "in-band source radiated energy / impact kinetic energy (lower bound of D1)",
     "radiated energy in the observed band from observed spectrum + transmission loss", "impact kinetic energy",
     "module band-by-band transmission loss", "module_tl", "Consistency check on D1; same chain rules as D1."),
    ("D3I", "implosion radiated energy / P V", "radiated acoustic energy", "hydrostatic pressure x volume (P V)",
     "near field, spherical spreading", "implosion_branch", "Separate implosion branch. Different denominator: never mix with impact coupling."),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def num(s):
    """first number in a text value (handles 1e-4, 3.4e-4 (z_s 30 m), 0.12-2.13% ...)."""
    if s is None or (isinstance(s, float) and np.isnan(s)): return None
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(s))
    if not m: return None
    v = float(m.group(0))
    return v / 100 if "%" in str(s) and "e" not in m.group(0).lower() else v


class B:
    def __init__(self, con): self.con, self.checks = con, []

    def ins(self, table, rows):
        if isinstance(rows, dict): rows = [rows]
        if not rows: return
        cols = list(rows[0].keys())
        self.con.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                             [[None if (isinstance(r.get(c), float) and np.isnan(r.get(c))) else r.get(c) for c in cols] for r in rows])

    def check(self, cid, desc, result, detail):
        res = result if isinstance(result, str) else ("PASS" if result else "FAIL")
        self.checks.append((cid, desc, res, detail))
        self.con.execute("DELETE FROM check_log WHERE check_id=?", (cid,))
        self.ins("check_log", dict(check_id=cid, description=desc, result=res, detail=detail, run_utc=BUILD_UTC))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True); ap.add_argument("--mod", required=True)
    ap.add_argument("--coupling", required=True); ap.add_argument("--record", required=True)
    a = ap.parse_args()
    mod, cdir = Path(a.mod), Path(a.coupling)
    rd = mod / "results-data"
    con = sqlite3.connect(a.db); b = B(con)
    for v in NEW_VIEWS: con.execute(f"DROP VIEW IF EXISTS {v}")
    for t in NEW_TABLES: con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute("DELETE FROM check_log WHERE check_id LIKE 'N%' OR check_id LIKE 'K%'")
    con.executescript(SCHEMA)
    reg = json.loads((mod / "registry" / "REGISTRY.json").read_text())
    ents = reg["entries"] if isinstance(reg["entries"], list) else list(reg["entries"].values())
    rstat = {e["id"]: e["status"] for e in ents}
    b.ins("quantity_def", [dict(quantity_id=q, name=n, unit=u, definition=d) for q, n, u, d in QUANTITIES])
    b.ins("coupling_definition", [dict(def_id=i, name=n, numerator=nu, denominator=de, propagation_relation=pr, allowed_chain=ch, rule=ru)
                                  for i, n, nu, de, pr, ch, ru in DEFINITIONS])
    sites = {r[0] for r in con.execute("SELECT site_id FROM site")}
    inputs = {}

    def reg_input(path, kind, entry=None, producer="module results-data", artifact=None, note=None):
        p = Path(path); h = sha(p)
        inputs[str(p)] = h
        rel = str(p.relative_to(mod)) if str(p).startswith(str(mod)) else "COUPLING:" + p.name
        b.ins("stage2_input", dict(file_path=rel, kind=kind, sha256=h, bytes=p.stat().st_size, producer=producer, artifact_version=artifact,
                                   registry_entry_id=entry, registry_status=rstat.get(entry, "UNREGISTERED" if entry is None else "UNKNOWN_ID"), note=note))
        return rel, h

    noise = []
    # ---- A. IMOS event-day noise measured from the raw files (note.imos_noise, CURRENT)
    f_b = rd / "imos1d" / "noise_bands.csv"; f_r = rd / "imos1d" / "noise_per_recording.csv"
    rel_b, h_b = reg_input(f_b, "noise: IMOS raw, per logger and band", "note.imos_noise")
    rel_r, h_r = reg_input(f_r, "noise: IMOS raw, per recording", "note.imos_noise")
    seg = pd.read_sql("""SELECT d.site_id, s.file_path, s.t_start_utc, s.t_end_utc FROM segment s JOIN dataset d USING(dataset_id)
                         WHERE d.site_id LIKE 'IMOS%' AND d.data_form='raw_waveform'""", con)
    seg["key"] = seg.file_path.str.replace("\\", "/").str.split("/").str[-2:].str.join("/")
    seg = seg.drop_duplicates("key").set_index("key")
    PR = pd.read_csv(f_r); bands = [c for c in PR.columns if re.fullmatch(r"\d+-\d+", c)]
    PR["key"] = PR.file.str.split("/").str[-2:].str.join("/")
    unmatched = int((~PR.key.isin(seg.index)).sum())
    span = {}
    for _, r in PR.iterrows():
        sid = f"IMOS{r.logger}"; s0 = seg.t_start_utc.get(r.key); s1 = seg.t_end_utc.get(r.key)
        span.setdefault(sid, []).extend([s0, s1])
        for bd in bands:
            lo, hi = (float(x) for x in bd.split("-"))
            noise.append(dict(site_id=sid, sensor_or_element=str(r.logger), context="MH370 8 Mar 2014", period_start_utc=s0, period_end_utc=s1,
                              period_note="one record (about 307 s)", band_lo_hz=lo, band_hi_hz=hi, band_label=f"{bd} Hz", quantity_id="band_mean_psd",
                              statistic="value", value=float(r[bd]), unit="dB re 1 uPa^2/Hz", original_value=float(r[bd]), original_unit="dB re 1 uPa^2/Hz",
                              original_field=bd, averaging="Welch (Hann) over one record", n_items=1, method="measured from raw recording",
                              source_id="imos_curtin_2014", dataset_id=None, segment_file=r.file, input_file=rel_r, input_sha256=h_r,
                              registry_entry_id="note.imos_noise", registry_status=rstat.get("note.imos_noise"), role="background (event day)",
                              caveat="2-5 Hz band is below the 8 Hz hardware high-pass corner" if lo < 8 else None))
    NB = pd.read_csv(f_b)
    for _, r in NB.iterrows():
        sid = f"IMOS{r.logger}"; lo, hi = (float(x) for x in r.band.split("-"))
        ss = [x for x in span.get(sid, []) if x]
        for fld, stat, avg, n in [("p5_1s", "p5", "1 s Hann periodograms", r.n_1s), ("p50_1s", "median", "1 s Hann periodograms", r.n_1s),
                                  ("p95_1s", "p95", "1 s Hann periodograms", r.n_1s), ("p5_welch", "p5", "Welch per record, across records", r.n_recordings),
                                  ("p50_welch", "median", "Welch per record, across records", r.n_recordings),
                                  ("p95_welch", "p95", "Welch per record, across records", r.n_recordings),
                                  ("p99_minus_p50_db", "p99_minus_median", "1 s Hann periodograms", r.n_1s)]:
            q = "level_spread" if fld.startswith("p99") else "band_mean_psd"
            noise.append(dict(site_id=sid, sensor_or_element=str(r.logger), context="MH370 8 Mar 2014", period_start_utc=min(ss) if ss else None,
                              period_end_utc=max(ss) if ss else None, period_note=f"{r.n_recordings} records, pre-registered background windows",
                              band_lo_hz=lo, band_hi_hz=hi, band_label=f"{r.band} Hz", quantity_id=q, statistic=stat, value=float(r[fld]),
                              unit="dB" if q == "level_spread" else "dB re 1 uPa^2/Hz", original_value=float(r[fld]),
                              original_unit="dB" if q == "level_spread" else "dB re 1 uPa^2/Hz", original_field=fld, averaging=avg, n_items=int(n),
                              method="measured from raw recording", source_id="imos_curtin_2014", dataset_id=None, segment_file=None,
                              input_file=rel_b, input_sha256=h_b, registry_entry_id="note.imos_noise", registry_status=rstat.get("note.imos_noise"),
                              role="background (event day)",
                              caveat="; ".join(x for x in ["below the 8 Hz hardware high-pass corner" if lo < 8 else None,
                                                           f"excess kurtosis of 1 s levels {r.excess_kurtosis_1s:.0f} (impulsive)" if r.excess_kurtosis_1s > 10 else None,
                                                           "roll-off flag" if bool(r.rolloff_flag) else None] if x) or None))
    # ---- B. IMS noise traced from Blackman 2004 App. B (note.ims_noise_blackman, CURRENT)
    f_bl = rd / "blackman_noise" / "blackman_noise_summary.json"
    rel_bl, h_bl = reg_input(f_bl, "noise: IMS traced from Blackman 2004 App. B", "note.ims_noise_blackman")
    BL = json.loads(f_bl.read_text())
    for st, d in BL["stations"].items():
        for fc, qd in d["psd_R_band_db"].items():
            fc = float(fc)
            for stat, k in [("p10", "q10"), ("median", "median"), ("p90", "q90")]:
                noise.append(dict(site_id=st, sensor_or_element="3-sensor mean", context="IMS 2003 Blackman cruise", period_start_utc=None,
                                  period_end_utc=None, period_note="2003 cruise; 6 s windows 20 s before predicted shot arrivals (Blackman p. 27)",
                                  band_lo_hz=round(fc * 2 ** (-1 / 6), 3), band_hi_hz=round(fc * 2 ** (1 / 6), 3), band_label=f"1/3 octave {fc:g} Hz",
                                  quantity_id="band_mean_psd", statistic=stat, value=float(qd[k]), unit="dB re 1 uPa^2/Hz", original_value=float(qd[k]),
                                  original_unit="dB re 1 uPa^2/Hz", original_field=f"psd_R_band_db.{fc:g}.{k}", averaging="6 s window; statistic over panels",
                                  n_items=int(d.get("n_ok", 0)), method="traced from published figure, converted with station calibration (route R)",
                                  source_id="blackman2004", dataset_id=None, segment_file=None, input_file=rel_bl, input_sha256=h_bl,
                                  registry_entry_id="note.ims_noise_blackman", registry_status=rstat.get("note.ims_noise_blackman"),
                                  role="background (2003; primary for IMS)", caveat="2003 levels, not 8 Mar 2014; calibration convention inferred"))
    # ---- C. Kadri 2024 Fig. 9 spectrogram backgrounds (digitised; unregistered sensitivity)
    kd = rd / "kadri_fig9_noise"
    rel_ks, h_ks = reg_input(kd / "summary.json", "noise: Kadri Fig 9 summary", None, note="not in REGISTRY.json")
    KS = json.loads((kd / "summary.json").read_text())
    for fn, st, cols, per in [("h01w_panel_b_bands_DIGITISED.csv", "H01W", [("psd_lin_mean_db", "mean"), ("psd_median_db", "median")], ("2014-03-08T00:27:00Z", "2014-03-08T00:57:00Z", "Fig. 9 panel b")),
                              ("h08s_panels_de_bands_DIGITISED.csv", "H08S", [("psd_lin_mean_db_d", "mean"), ("psd_median_db_d", "median"),
                                                                              ("psd_lin_mean_db_e", "mean"), ("psd_median_db_e", "median")], ("2014-03-08T01:00:00Z", "2014-03-08T01:20:00Z", "Fig. 9 panels d, e"))]:
        rel_k, h_k = reg_input(kd / fn, "noise: Kadri Fig 9 spectrogram bands (digitised)", None, note="not in REGISTRY.json")
        K = pd.read_csv(kd / fn)
        for _, r in K.iterrows():
            for c, stat in cols:
                panel = per[2] if st == "H01W" else f"Fig. 9 panel {c[-1]}"
                noise.append(dict(site_id=st, sensor_or_element=panel, context="MH370 8 Mar 2014", period_start_utc=per[0], period_end_utc=per[1],
                                  period_note=panel, band_lo_hz=round(r.fc_hz * 2 ** (-1 / 6), 3), band_hi_hz=round(r.fc_hz * 2 ** (1 / 6), 3),
                                  band_label=f"1/3 octave {r.fc_hz:g} Hz", quantity_id="band_mean_psd", statistic=stat, value=float(r[c]),
                                  unit="dB re 1 uPa^2/Hz", original_value=float(r[c]), original_unit="dB re 1 uPa^2/Hz", original_field=c,
                                  averaging="spectrogram colour over the panel", n_items=None, method="digitised from published spectrogram colour",
                                  source_id="kadri2024", dataset_id=None, segment_file=None, input_file=rel_k, input_sha256=h_k,
                                  registry_entry_id=None, registry_status="UNREGISTERED",
                                  role="sensitivity (" + KS[st]["rule_outcome"].split(":")[-1].strip() + ")",
                                  caveat="biased low: 64 dB colour floor and JPEG darkening (summary.json)" if st == "H01W" else
                                  "periodic impulses every 10-15 s in both panels (airgun survey)"))
    # ---- D. Metz 2023 H11 envelope background (digitised; calibration context)
    f_m = rd / "metz_f35a" / "obs_summary.json"
    rel_m, h_m = reg_input(f_m, "noise: Metz Fig 3C/D envelope background (digitised)", "note.metz_f35a_anchor")
    MS = json.loads(f_m.read_text())
    for tri, d in MS["triads"].items():
        noise.append(dict(site_id=tri, sensor_or_element="triad mean of elements", context="calibration: F-35A 9 Apr 2019", period_start_utc="2019-04-09T11:02:55Z",
                          period_end_utc="2019-04-09T11:04:25Z", period_note="Metz Fig. 3C/D window, outside the arrival", band_lo_hz=4.0, band_hi_hz=64.0,
                          band_label="4-64 Hz", quantity_id="rms_level", statistic="median", value=float(d["noise_db_mean"]), unit="dB re 1 uPa",
                          original_value=float(d["noise_db_mean"]), original_unit="dB re 1 uPa", original_field="triads.noise_db_mean",
                          averaging="1 s RMS envelope; median outside the arrival per element, mean over elements", n_items=3,
                          method="digitised from published envelope", source_id="metz2023", dataset_id="metz2023_fig3cd_h11", segment_file=None,
                          input_file=rel_m, input_sha256=h_m, registry_entry_id="note.metz_f35a_anchor", registry_status=rstat.get("note.metz_f35a_anchor"),
                          role="background at the F-35A calibration receivers", caveat=None))
    b.ins("noise_estimate", noise)
    b.ins("noise_condition", [
        dict(site_id="H08S", context="MH370 8 Mar 2014", condition="periodic airgun shots (about every 10 s) in the Kadri Fig. 9 panels; 110 shots 01:00-01:19 UTC",
             effect="masking and false alarms; a shot coincidence is a label, not an exclusion (Pete, 23 Oct 2026)", source="kadri_fig9_noise/summary.json; h08s_template_shots.csv",
             input_file=rel_ks),
        dict(site_id="OHASISBIO (all)", context="MH370 8 Mar 2014", condition="powerful seismic shots from an exploration survey obscure most of the data that day",
             effect="raised noise and masking at the OHASISBIO sites; no calibrated level extracted yet", source="Royer 2016, LDO-201608, p. 3", input_file=None),
        dict(site_id="IMOS (all)", context="MH370 8 Mar 2014", condition="8 Hz hardware high-pass corner (header LF); 2-5 Hz band below it",
             effect="2-5 Hz levels are not ambient-noise estimates", source="record headers; imos1d", input_file=rel_b),
        dict(site_id="H01W, H08S, H08N", context="IMS 2003 Blackman cruise", condition="2003 levels, not 8 Mar 2014",
             effect="use as background estimate with that label; Kadri Fig. 9 gives an 8 Mar 2014 sensitivity", source="note.ims_noise_blackman", input_file=rel_bl)])

    # ---- coupling inputs (from the coupling thread; never edited here)
    man = pd.read_csv(cdir / "MANIFEST.tsv", sep="\t")
    man_ok = []
    for _, r in man.iterrows():
        p = cdir / r.file; ok = p.exists() and sha(p) == r.sha256; man_ok.append((r.file, ok))
        reg_input(p, "coupling input: " + r.role, None, producer=r.producer, artifact=r.artifact_version)
    def defid(s):
        s = str(s)
        if "implosion" in s: return "D3I"
        m = re.match(r"(D\d)", s); return m.group(1) if m else None
    PRV = pd.read_csv(cdir / "coupling-prior-range.csv"); h_pr = sha(cdir / "coupling-prior-range.csv")
    rows = []
    for _, r in PRV.iterrows():
        role = str(r.role_in_prior)
        status = ("EXCLUDED" if role.lower().startswith("exclude") else "SUPERSEDED" if role.lower().startswith("superseded")
                  else "PROPOSAL (not ruled)" if role.upper().startswith("PRIOR") else "EVIDENCE")
        f35 = PETE_F35 if str(r.value_id).startswith("F35") else None
        rows.append(dict(value_id=r.value_id, def_id=defid(r.definition_class), definition_as_written=r.definition_class, value_as_written=str(r.value),
                         value_num=num(r.value) if str(r.value) != "log-uniform" else None, range_low=num(r.range_low), range_high=num(r.range_high),
                         numerator=r.numerator, denominator=r.denominator, band_hz=None if pd.isna(r.band_Hz) else str(r.band_Hz),
                         source_depth_m=None if pd.isna(r.source_depth_m) else str(r.source_depth_m), mechanism_and_scale=r.mechanism_and_scale,
                         propagation_relation_required=r.propagation_relation_required, reference=r.reference,
                         read_in_primary_as_written=None if pd.isna(r.read_in_primary) else str(r.read_in_primary), role_in_prior=role,
                         role_status=status, evidence_id={"F35-BROWN": "E05", "F35-BROWN-REPRO": "E05", "F35-PROJ-22OCT": "E01", "F35-PROJ-09OCT": "E01",
                                                          "F35-PROJ-INBAND": "E01"}.get(r.value_id), f35a_note=f35,
                         notes=r.notes, input_file="COUPLING:coupling-prior-range.csv", input_sha256=h_pr))
    b.ins("coupling_value", rows)
    REG = pd.read_csv(cdir / "coupling-evidence-register.csv"); h_rg = sha(cdir / "coupling-evidence-register.csv")
    b.ins("coupling_evidence", [dict(**{c: (None if pd.isna(r[c]) else str(r[c])) for c in REG.columns}, input_file="COUPLING:coupling-evidence-register.csv",
                                     input_sha256=h_rg) for _, r in REG.iterrows()])
    ISP = pd.read_csv(cdir / "impact-source-parameters.csv")
    ISP.to_sql("cp_impact_source_parameters", con, index=False)
    con.execute("DELETE FROM imported_table WHERE table_name='cp_impact_source_parameters'")
    b.ins("imported_table", dict(table_name="cp_impact_source_parameters", source_file="COUPLING:impact-source-parameters.csv",
                                 sha256=sha(cdir / "impact-source-parameters.csv"), n_rows=len(ISP), n_cols=ISP.shape[1],
                                 header_comment="56 source-parameter rows per event or study and quantity (coupling thread, 23 Oct 2026)", dataset_id=None))
    # curves
    curve = []
    E1 = pd.read_csv(rd / "metz_f35a" / "step2_eta.csv"); reg_input(rd / "metz_f35a" / "step2_eta.csv", "coupling curve E01 (far field)", "note.metz_f35a_anchor")
    for r in E1.itertuples():
        curve.append(dict(curve_id="E01_far_field_H11", evidence_id="E01", def_id="D1", station=r.triad, path_or_point=r.path, bottom=None, src_depth_m=r.src_depth_m,
                          tl_model=r.tl, tau_s=r.tau_s, spectral_slope=r.slope, energy_case=r.E, noise_def=None, template=None, eta=r.eta,
                          definition_as_written="D1, module chain (metz_f35a step 2)", input_file="results-data/metz_f35a/step2_eta.csv",
                          registry_entry_id="note.metz_f35a_anchor", registry_status=rstat.get("note.metz_f35a_anchor"), status_note=PETE_F35))
    NF = pd.read_csv(cdir / "metz-nearfield-eta.csv")
    for r in NF.itertuples():
        curve.append(dict(curve_id="E02_near_field_cabled", evidence_id="E02", def_id="D1", station=r.station, path_or_point=r.source_point, bottom=r.bottom,
                          src_depth_m=r.src_depth_m, tl_model="KRAKEN (surface image)", tau_s=r.tau_s, spectral_slope=r.slope, energy_case=r.E,
                          noise_def=r.noise_def, template=None, eta=r.eta, definition_as_written=r.definition, input_file="COUPLING:metz-nearfield-eta.csv",
                          registry_entry_id=None, registry_status="UNREGISTERED",
                          status_note="Model-error measure for the propagation chain (register E02); not an independent coupling estimate"))
    C9 = pd.read_csv(rd / "f35a_cal" / "eta_cal.csv"); reg_input(rd / "f35a_cal" / "eta_cal.csv", "coupling curve, 9 Oct calibration", "note.f35a_eta_calibration")
    for r in C9.itertuples():
        curve.append(dict(curve_id="E01_far_field_9oct", evidence_id="E01", def_id="D1", station=r.station, path_or_point=None, bottom=None, src_depth_m=r.src_depth_m,
                          tl_model="KRAKEN (no RAM)", tau_s=r.tau_s, spectral_slope=r.slope, energy_case=r.E_case, noise_def=None, template=r.template, eta=r.eta_cal,
                          definition_as_written="D1, 9 Oct calibration (peak-to-exposure template)", input_file="results-data/f35a_cal/eta_cal.csv",
                          registry_entry_id="note.f35a_eta_calibration", registry_status=rstat.get("note.f35a_eta_calibration"),
                          status_note="SUPERSEDED by E01_far_field_H11 (registry note.f35a_eta_calibration)"))
    b.ins("coupling_curve", curve)
    con.executescript(VIEWS)

    # ---------------- checks
    q = lambda s: con.execute(s).fetchall()
    units = dict(q("SELECT quantity_id, unit FROM quantity_def"))
    bad_u = q("SELECT noise_id, quantity_id, unit FROM noise_estimate") ; bad_u = [x for x in bad_u if units.get(x[1]) != x[2]]
    b.check("N01", "Every noise value uses a declared quantity and its unit", not bad_u, f"{len(bad_u)} mismatches")
    bad_b = q("SELECT count(*) FROM noise_estimate WHERE NOT (band_lo_hz < band_hi_hz)")[0][0]
    b.check("N02", "Every noise band has lower edge < upper edge", bad_b == 0, f"{bad_b} bad bands")
    out = q("SELECT count(*) FROM noise_estimate WHERE quantity_id='band_mean_psd' AND (value < 40 OR value > 140)")[0][0]
    b.check("N03", "Noise PSD values inside 40-140 dB re 1 uPa^2/Hz (plausibility)", out == 0, f"{out} outside")
    # N04 round trip IMOS band stats
    db_nb = pd.read_sql("SELECT sensor_or_element logger, band_label, original_field, value FROM noise_estimate WHERE input_file=?", con, params=(rel_b,))
    mism = 0
    for _, r in NB.iterrows():
        for fld in ["p5_1s", "p50_1s", "p95_1s", "p5_welch", "p50_welch", "p95_welch", "p99_minus_p50_db"]:
            v = db_nb[(db_nb.logger == str(r.logger)) & (db_nb.band_label == f"{r.band} Hz") & (db_nb.original_field == fld)].value
            mism += int(len(v) != 1 or abs(float(v.iloc[0]) - float(r[fld])) > 1e-9)
    b.check("N04", "IMOS band statistics in the database equal noise_bands.csv (round trip)", mism == 0, f"{len(NB) * 7} values, {mism} mismatches")
    gate = q("SELECT count(*) FROM noise_estimate WHERE source_id='blackman2004' AND statistic='median' AND (value<55 OR value>105)")[0][0]
    b.check("N05", "Blackman medians 5-40 Hz inside the pre-registered 55-105 dB gate", gate == 0, f"{gate} outside")
    bad_h = [p for p, h in inputs.items() if sha(p) != h]
    b.check("N06", "Every stage-2 input file still matches its SHA-256", not bad_h, f"{len(inputs)} files, {len(bad_h)} changed")
    b.check("N07", "Every IMOS per-record noise row links to a raw record in table segment", unmatched == 0, f"{len(PR)} records, {unmatched} unmatched")
    bad_s = q("SELECT DISTINCT site_id FROM noise_estimate"); bad_s = [x[0] for x in bad_s if x[0] not in sites]
    b.check("N08", "Every noise row names a site in table site", not bad_s, f"unknown: {bad_s}")
    b.check("K01", "Every coupling value has a declared definition", q("SELECT count(*) FROM coupling_value WHERE def_id IS NULL OR def_id NOT IN (SELECT def_id FROM coupling_definition)")[0][0] == 0,
            "; ".join(f"{r[0]}->{r[1]}" for r in q("SELECT value_id, def_id FROM coupling_value")))
    k2 = q("SELECT count(*) FROM v_coupling_for_module_chain WHERE def_id NOT IN ('D1','D4')")[0][0]
    b.check("K02", "Module-chain view holds no path-blind, near-field or implosion value", k2 == 0, f"{k2} wrong rows")
    k3 = q("SELECT count(*) FROM v_coupling_path_blind WHERE def_id != 'D2'")[0][0]
    b.check("K03", "Path-blind view holds only Arons-equivalent values", k3 == 0, f"{k3} wrong rows")
    k4 = q("SELECT value_id, denominator FROM coupling_value WHERE def_id='D3I'")
    b.check("K04", "Implosion values use the P V denominator and stay out of the impact views", all("P V" in (d or "") for _, d in k4) and len(k4) > 0, str(k4))
    anchor = json.loads((rd / "metz_f35a" / "step2_summary.json").read_text())["anchor_eta"]
    sub = pd.read_sql("""SELECT station, tau_s, eta FROM coupling_curve WHERE curve_id='E01_far_field_H11' AND path_or_point='primary'
                         AND src_depth_m=10 AND spectral_slope=2 AND energy_case='mid' AND tl_model='ram'""", con)
    sub = sub[np.isclose(sub.tau_s, sub.tau_s.iloc[(sub.tau_s - 10).abs().argmin()])]
    gm = float(np.exp(np.log(sub.eta).mean())) if len(sub) == 2 else float("nan")
    b.check("K05", "Recomputed from the far-field curve, the 10 m point (geometric mean H11N/H11S, slope 2, mid energy, KRAKEN+RAM, tau 10 s) equals step2_summary anchor_eta",
            abs(gm - anchor) / anchor < 1e-3, f"recomputed {gm:.6g}; anchor {anchor:.6g}; rows {len(sub)}")
    t1 = q("SELECT what_it_constrains FROM coupling_evidence WHERE evidence_id='E01'")[0][0]; t2 = q("SELECT what_it_constrains FROM coupling_evidence WHERE evidence_id='E02'")[0][0]
    far = [float(x) for x in re.search(r"([\d.e-]+) / ([\d.e-]+) / ([\d.e-]+)", t1).groups()]
    near = [float(x) for x in re.search(r"([\d.e-]+) / ([\d.e-]+) / ([\d.e-]+)", t2).groups()]
    ratio = [n_ / f_ for n_, f_ in zip(near, far)]
    b.check("K06", "Register E02/E01 ridge ratio is about 2.0 at 2, 10 and 30 m (same KRAKEN+RAM chain)", all(1.9 <= x <= 2.1 for x in ratio), f"ratios {[round(x, 3) for x in ratio]}")
    k10 = q("SELECT count(*) FROM v_coupling_for_module_chain WHERE item LIKE 'E02%' OR item LIKE '%9oct%'")[0][0]
    b.check("K10", "Module-chain view holds no model-error curve (E02) and no superseded curve", k10 == 0, f"{k10} wrong rows")
    over = pd.read_sql("""SELECT curve_id, src_depth_m, spectral_slope, count(*) n, min(tau_s) tau_min, max(tau_s) tau_max, max(eta) eta_max
                          FROM coupling_curve WHERE eta > 1 GROUP BY curve_id, src_depth_m, spectral_slope""", con)
    tot = q("SELECT count(*) FROM coupling_curve")[0][0]
    b.check("K11", "Coupling curve rows above 1 (more acoustic energy than kinetic energy: physically impossible) - listed; such parameter combinations are ruled out by the data",
            "REVIEW" if len(over) else "PASS",
            f"{int(over.n.sum()) if len(over) else 0} of {tot} rows: " + "; ".join(f"{r.curve_id} z={r.src_depth_m:g} m slope {r.spectral_slope:g}: {r.n} rows, tau {r.tau_min:.3g}-{r.tau_max:.3g} s, max {r.eta_max:.3g}" for r in over.itertuples()))
    b.check("K07", "Coupling inputs match MANIFEST.tsv SHA-256", all(ok for _, ok in man_ok), str(man_ok))
    g1 = q("SELECT evidence_id, how_it_is_used FROM coupling_evidence WHERE independence_group LIKE 'G1%' OR independence_group='G1'")
    b.check("K08", "F-35A evidence items share one independence group and only E01 is the likelihood term", sum("LIKELIHOOD TERM (the primary" in (u or "") for _, u in g1) == 1,
            "; ".join(f"{e}: {u[:40]}" for e, u in g1))
    hits = []
    for tbl, idc, cols in [("coupling_value", "value_id", ["read_in_primary_as_written", "notes", "reference"]),
                           ("coupling_evidence", "evidence_id", ["evidence", "source", "main_error_terms"]),
                           ("cp_impact_source_parameters", "event_or_study", ["read_in_primary", "copy_location", "notes"])]:
        for row in q(f"SELECT {idc}, {', '.join(cols)} FROM {tbl}"):
            for c, v in zip(cols, row[1:]):
                for w in RESTRICTIVE:
                    if v and w in str(v).lower(): hits.append(f"{tbl}.{c} [{row[0]}]: '{w}'")
    b.check("K09", "Text that limits or discounts a source, listed for Pete (label rule 22 Oct 2026); nothing is excluded by it",
            "REVIEW" if hits else "PASS", "; ".join(sorted(set(hits))) or "none")
    con.execute("DELETE FROM meta WHERE key LIKE 'stage2_%'")
    for k, v in dict(stage2_schema=STAGE, stage2_built_utc=BUILD_UTC,
                     stage2_scope="Noise and coupling: values as measured/traced/digitised/published with definition, unit, source file and SHA-256. "
                                  "Coupling content comes from the coupling thread (session c764a583) via MANIFEST.tsv; F-35A values are points on one curve, no ruling needed (Pete, 24 Oct 2026).",
                     stage2_run_order="build_hydro_data_db.py -> build_noise_coupling.py -> arc_line_of_sight.py -> arc_station_count.py -> make_sites_map.py / arc_recording_opportunity.py").items():
        b.ins("meta", dict(key=k, value=v))
    con.commit()
    write_record(con, a.record, b.checks)
    con.close()
    for c in b.checks: print(f"{c[0]} {c[2]:6s} {c[1]} | {c[3][:150]}")


def write_record(con, path, checks):
    q = lambda s: pd.read_sql(s, con)
    L = [f"# Noise and acoustic coupling: generated record", "",
         f"Generated from `hydro_data.sqlite` by `build_noise_coupling.py` on {BUILD_UTC}. Do not edit by hand; rebuild instead.", "",
         "**Rules.** Every value carries its definition, unit, source file and SHA-256. Coupling values are used only with the propagation relation "
         "of their definition (views `v_coupling_for_module_chain`, `v_coupling_path_blind`, `v_coupling_implosion`). The F-35A values are points on "
         "one (coupling, source depth, spectrum) curve from one recording; no ruling is needed (Pete, 24 Oct 2026). Status and defects stay in the registry.", "",
         "## 1. Background noise, median band level by site (dB re 1 uPa^2/Hz unless stated)", ""]
    ns = q("""SELECT site_id, context, band_label, statistic, round(value,1) v, unit, averaging, role FROM noise_estimate
              WHERE statistic='median' ORDER BY context, site_id, band_lo_hz""")
    for (ctx, avg), g in ns.groupby(["context", "averaging"], sort=False):
        piv = g.pivot_table(index="site_id", columns="band_label", values="v", aggfunc="first")
        piv = piv[sorted(piv.columns, key=lambda c: num(c.replace("1/3 octave ", "")))]
        L += [f"**{ctx}; {avg}; unit {g.unit.iloc[0]}; role: {g.role.iloc[0]}**", "", piv.to_markdown(), ""]
    L += ["## 2. Conditions that affect noise", "", q("SELECT site_id, context, condition, effect, source FROM noise_condition").to_markdown(index=False), "",
          "## 3. Coupling definitions", "", q("SELECT def_id, name, allowed_chain, rule FROM coupling_definition").to_markdown(index=False), "",
          "## 4. Coupling values (as published or derived; status)", "",
          q("SELECT value_id, def_id, value_as_written, range_low, range_high, role_in_prior, role_status FROM coupling_value").to_markdown(index=False), "",
          "## 5. F-35A coupling curve against source depth (module chain, register E01; E02 near field for model error)", ""]
    cv = q("""SELECT curve_id, src_depth_m, count(*) n, min(eta) eta_min, max(eta) eta_max FROM coupling_curve GROUP BY curve_id, src_depth_m
              ORDER BY curve_id, src_depth_m""")
    L += [cv.to_markdown(index=False, floatfmt=".3g"), "", "## 6. Evidence register (roles and independence groups)", "",
          q("SELECT evidence_id, evidence, how_it_is_used, independence_group FROM coupling_evidence").to_markdown(index=False), "",
          "## 7. Checks", "", "| check | result | description | detail |", "|---|---|---|---|"]
    L += [f"| {c[0]} | {c[2]} | {c[1]} | {c[3][:300].replace('|', '/')} |" for c in checks]
    Path(path).write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
