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
  * Coupling tables are the coupling thread's package (25 Oct 2026), imported unchanged and validated in every build by its
    own validate_coupling_tables.py: each definition class pairs only with its allowed propagation chain; the module-chain
    view never returns an Arons-equivalent (D2) or land-seismic (S1) value; no value is an "anchor".
  * The F-35A values are points on one (coupling, source depth, spectrum) curve from one recording. No ruling is needed
    (Pete, 24 Oct 2026: "The F35 ruling was a red herring").
  * Text that limits or discounts a source ("not held", "closed", "paywalled", "no legitimate copy") is listed for Pete
    in check K09 (standing rule on labels, 22 Oct 2026); it is not used to exclude anything.
"""
import argparse, hashlib, json, re, sqlite3, sys, textwrap
sys.dont_write_bytecode = True
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STAGE = "noise-coupling v1"
THIRD_OCT = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
RESTRICTIVE = ["not held", "closed access", "(closed)", "paywalled", "paywall", "unobtainable", "no legitimate copy", "unusable", "restricted"]
PETE_F35 = "One point on the F-35A (coupling, source depth, spectrum) curve from one recording; no ruling needed (Pete, 24 Oct 2026: 'The F35 ruling was a red herring')."

PKG_TABLES = {"coupling_evidence": "db_coupling_evidence.csv", "coupling_value": "db_coupling_value.csv", "coupling_family": "db_coupling_family.csv",
              "coupling_family_element_evidence": "db_family_element_evidence.csv", "impact_case": "db_impact_case.csv",
              "reference_event": "db_reference_event.csv", "received_observation": "db_received_observation.csv",
              "data_availability_probe": "db_data_availability_probe.csv"}
NEW_TABLES = ["quantity_def", "noise_estimate", "noise_condition", "coupling_definition", "coupling_curve", "cp_impact_source_parameters",
              "cp_coupling_prior_range_2026_10_23", "stage2_input"] + list(PKG_TABLES)
NEW_VIEWS = ["v_noise_summary", "v_noise_8mar2014", "v_coupling_for_module_chain", "v_coupling_path_blind", "v_coupling_implosion",
             "v_module_chain", "v_arons_screen", "v_envelope", "v_cross_check", "v_coupling_curve_module"]

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
  definition_class TEXT NOT NULL, allowed_chain TEXT NOT NULL, source TEXT NOT NULL, PRIMARY KEY (definition_class, allowed_chain));
CREATE TABLE coupling_curve (
  curve_row INTEGER PRIMARY KEY, curve_id TEXT NOT NULL, evidence_id TEXT, definition_class TEXT NOT NULL, propagation_chain TEXT NOT NULL,
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
CREATE VIEW v_module_chain AS SELECT * FROM coupling_value
  WHERE propagation_chain_required LIKE 'MODULE_%' AND status = 'EVIDENCE';
CREATE VIEW v_arons_screen AS SELECT * FROM coupling_value
  WHERE propagation_chain_required = 'ARONS_1954' AND status = 'EVIDENCE';
CREATE VIEW v_envelope AS SELECT * FROM coupling_value
  WHERE role = 'ENVELOPE_AND_SCALING' AND status = 'EVIDENCE';
CREATE VIEW v_cross_check AS SELECT * FROM coupling_value WHERE definition_class = 'S1';
CREATE VIEW v_coupling_curve_module AS
SELECT c.curve_id, c.evidence_id, c.definition_class, c.propagation_chain, c.src_depth_m, count(*) AS n_rows, min(c.eta) AS eta_min, max(c.eta) AS eta_max
FROM coupling_curve c JOIN coupling_evidence e ON e.evidence_id = c.evidence_id
WHERE c.propagation_chain LIKE 'MODULE_%' AND c.status_note NOT LIKE 'SUPERSEDED%' AND e.how_it_is_used LIKE 'LIKELIHOOD TERM%'
GROUP BY c.curve_id, c.src_depth_m;
"""
QUANTITIES = [
    ("band_mean_psd", "band-averaged noise power spectral density", "dB re 1 uPa^2/Hz",
     "10 log10 of the mean of the linear PSD over the band; Welch or periodogram estimate as stated in 'averaging'."),
    ("rms_level", "RMS sound pressure level in a band", "dB re 1 uPa",
     "20 log10 of the RMS pressure over the stated averaging window and band."),
    ("level_spread", "level difference", "dB", "Difference between two statistics of the same level series (for example p99 minus median)."),
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

    # ---- coupling inputs (coupling thread, session c764a583; package 25 Oct 2026; never edited here)
    man = pd.read_csv(cdir / "MANIFEST.tsv", sep="\t")
    man_ok = []
    for _, r in man.iterrows():
        p = cdir / r.file; ok = p.exists() and sha(p) == r.sha256; man_ok.append((r.file, ok))
        reg_input(p, "coupling input: " + r.role, None, producer=r.producer, artifact=r.artifact_version)
    import importlib.util as _ilu, subprocess, sys as _sys
    _sp = _ilu.spec_from_file_location("vct", cdir / "validate_coupling_tables.py"); V = _ilu.module_from_spec(_sp); _sp.loader.exec_module(V)
    assert V.FILES == PKG_TABLES | {} or set(V.FILES.values()) == set(PKG_TABLES.values()), "package file list changed; update PKG_TABLES"
    vr = subprocess.run([_sys.executable, str(cdir / "validate_coupling_tables.py"), str(cdir)], capture_output=True, text=True)
    b.ins("coupling_definition", [dict(definition_class=k, allowed_chain=c, source="validate_coupling_tables.py CHAIN_FOR_CLASS")
                                  for k, cs in V.CHAIN_FOR_CLASS.items() for c in sorted(cs)])
    for t, f in PKG_TABLES.items():
        df = pd.read_csv(cdir / f); df["input_file"] = "COUPLING:" + f; df["input_sha256"] = sha(cdir / f)
        df.to_sql(t, con, index=False)
    PRV = pd.read_csv(cdir / "coupling-prior-range.csv"); PRV["superseded_by"] = "coupling package 25 Oct 2026 (db_coupling_value.csv)"
    PRV.to_sql("cp_coupling_prior_range_2026_10_23", con, index=False)
    ISP = pd.read_csv(cdir / "impact-source-parameters.csv")
    ISP.to_sql("cp_impact_source_parameters", con, index=False)
    con.execute("DELETE FROM imported_table WHERE table_name IN ('cp_impact_source_parameters', 'cp_coupling_prior_range_2026_10_23')")
    b.ins("imported_table", [dict(table_name="cp_impact_source_parameters", source_file="COUPLING:impact-source-parameters.csv",
                                  sha256=sha(cdir / "impact-source-parameters.csv"), n_rows=len(ISP), n_cols=ISP.shape[1],
                                  header_comment="56 source-parameter rows per event or study and quantity (coupling thread, 23 Oct 2026)", dataset_id=None),
                             dict(table_name="cp_coupling_prior_range_2026_10_23", source_file="COUPLING:coupling-prior-range.csv",
                                  sha256=sha(cdir / "coupling-prior-range.csv"), n_rows=len(PRV), n_cols=PRV.shape[1],
                                  header_comment="SUPERSEDED by the 25 Oct 2026 package; kept verbatim for provenance", dataset_id=None)])
    # raw H11 background from the package (received_observation) into noise_estimate, original value in Pa kept
    RO = pd.read_csv(cdir / "db_received_observation.csv"); h_ro = sha(cdir / "db_received_observation.csv")
    b.ins("noise_estimate", [dict(site_id=r.station[:4], sensor_or_element=r.station, context="calibration: F-35A 9 Apr 2019", period_start_utc="2019-04-09T10:50:00Z",
                                  period_end_utc="2019-04-09T11:20:00Z", period_note="raw EarthScope record 10:50-11:20 UTC", band_lo_hz=float(r.band_Hz.split("-")[0]),
                                  band_hi_hz=float(r.band_Hz.split("-")[1]), band_label=f"{r.band_Hz} Hz", quantity_id="rms_level", statistic="median",
                                  value=20 * np.log10(r.median_1sRMS_Pa / 1e-6), unit="dB re 1 uPa", original_value=float(r.median_1sRMS_Pa), original_unit="Pa",
                                  original_field="median_1sRMS_Pa", averaging="1 s moving RMS; median over the record", n_items=None,
                                  method="measured from raw recording (EarthScope, response removed)", source_id="metz2023", dataset_id=None, segment_file=None,
                                  input_file="COUPLING:db_received_observation.csv", input_sha256=h_ro, registry_entry_id=None, registry_status="UNREGISTERED",
                                  role="background at the F-35A calibration receivers (raw)", caveat=r.method) for r in RO.itertuples()])
    # curves (this database's part: the F-35A ridge in full)
    curve = []
    E1 = pd.read_csv(rd / "metz_f35a" / "step2_eta.csv"); reg_input(rd / "metz_f35a" / "step2_eta.csv", "coupling curve E01 (far field)", "note.metz_f35a_anchor")
    for r in E1.itertuples():
        curve.append(dict(curve_id="E01_far_field_H11", evidence_id="E01", definition_class="D1",
                          propagation_chain="MODULE_KRAKEN_RAM" if r.tl == "ram" else "MODULE_KRAKEN_ONLY", station=r.triad, path_or_point=r.path, bottom=None,
                          src_depth_m=r.src_depth_m, tl_model=r.tl, tau_s=r.tau_s, spectral_slope=r.slope, energy_case=r.E, noise_def=None, template=None, eta=r.eta,
                          definition_as_written="D1, module chain (metz_f35a step 2)", input_file="results-data/metz_f35a/step2_eta.csv",
                          registry_entry_id="note.metz_f35a_anchor", registry_status=rstat.get("note.metz_f35a_anchor"), status_note=PETE_F35))
    NF = pd.read_csv(cdir / "metz-nearfield-eta.csv")
    for r in NF.itertuples():
        curve.append(dict(curve_id="E02_near_field_cabled", evidence_id="E02", definition_class="D1", propagation_chain="MODULE_KRAKEN_ONLY", station=r.station,
                          path_or_point=r.source_point, bottom=r.bottom, src_depth_m=r.src_depth_m, tl_model="KRAKEN (surface image)", tau_s=r.tau_s,
                          spectral_slope=r.slope, energy_case=r.E, noise_def=r.noise_def, template=None, eta=r.eta, definition_as_written=r.definition,
                          input_file="COUPLING:metz-nearfield-eta.csv", registry_entry_id=None, registry_status="UNREGISTERED",
                          status_note="Model-error measure for the propagation chain (evidence E02); not an independent coupling estimate"))
    C9 = pd.read_csv(rd / "f35a_cal" / "eta_cal.csv"); reg_input(rd / "f35a_cal" / "eta_cal.csv", "coupling curve, 9 Oct calibration", "note.f35a_eta_calibration")
    for r in C9.itertuples():
        curve.append(dict(curve_id="E01_far_field_9oct", evidence_id="E01", definition_class="D1", propagation_chain="MODULE_KRAKEN_ONLY", station=r.station,
                          path_or_point=None, bottom=None, src_depth_m=r.src_depth_m, tl_model="KRAKEN (no RAM)", tau_s=r.tau_s, spectral_slope=r.slope,
                          energy_case=r.E_case, noise_def=None, template=r.template, eta=r.eta_cal,
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
    vlines = [l for l in vr.stdout.splitlines() if l.startswith(("PASS", "FAIL", "RESULT", "  v_"))]
    b.check("K01", "Coupling package validator (validate_coupling_tables.py, coupling thread) passes", vr.returncode == 0 and "RESULT: PASS" in vr.stdout,
            "; ".join(vlines)[:900])
    k2 = q("SELECT count(*) FROM v_module_chain WHERE definition_class NOT IN ('D1','D3','D4')")[0][0]
    b.check("K02", "Module-chain view holds no Arons-equivalent (D2) or land-seismic (S1) value", k2 == 0, f"{k2} wrong rows")
    k3 = q("SELECT count(*) FROM v_arons_screen WHERE definition_class != 'D2'")[0][0]
    b.check("K03", "Arons view holds only D2 values", k3 == 0, f"{k3} wrong rows")
    pairs = {(c, ch) for c, ch in q("SELECT definition_class, allowed_chain FROM coupling_definition")}
    badc = q("SELECT curve_id, definition_class, propagation_chain FROM coupling_curve GROUP BY 1,2,3")
    badc = [x for x in badc if (x[1], x[2]) not in pairs]
    b.check("K04", "Every coupling-curve row uses an allowed (definition class, chain) pair", not badc, str(badc))
    anchor = json.loads((rd / "metz_f35a" / "step2_summary.json").read_text())["anchor_eta"]
    sub = pd.read_sql("""SELECT station, tau_s, eta FROM coupling_curve WHERE curve_id='E01_far_field_H11' AND path_or_point='primary'
                         AND src_depth_m=10 AND spectral_slope=2 AND energy_case='mid' AND tl_model='ram'""", con)
    sub = sub[np.isclose(sub.tau_s, sub.tau_s.iloc[(sub.tau_s - 10).abs().argmin()])]
    gm = float(np.exp(np.log(sub.eta).mean())) if len(sub) == 2 else float("nan")
    cv02 = q("SELECT value FROM coupling_value WHERE evidence_id='E01' AND source_depth_m=10 AND propagation_chain_required='MODULE_KRAKEN_RAM' AND definition_class='D1'")
    b.check("K05", "The 10 m F-35A ridge point recomputed from the curve (geometric mean H11N/H11S, slope 2, mid energy, KRAKEN+RAM, tau 10 s) "
            "equals step2_summary and the package value", abs(gm - anchor) / anchor < 1e-3 and any(abs(v[0] - gm) / gm < 0.01 for v in cv02),
            f"recomputed {gm:.6g}; step2_summary {anchor:.6g}; package {[v[0] for v in cv02]}")
    t1 = q("SELECT what_it_constrains FROM coupling_evidence WHERE evidence_id='E01'")[0][0]; t2 = q("SELECT what_it_constrains FROM coupling_evidence WHERE evidence_id='E02'")[0][0]
    far = [float(x) for x in re.search(r"([\d.e-]+) / ([\d.e-]+) / ([\d.e-]+)", t1).groups()]
    near = [float(x) for x in re.search(r"([\d.e-]+) / ([\d.e-]+) / ([\d.e-]+)", t2).groups()]
    ratio = [n_ / f_ for n_, f_ in zip(near, far)]
    b.check("K06", "Evidence E02/E01 ridge ratio is about 2.0 at 2, 10 and 30 m (same KRAKEN+RAM chain)", all(1.9 <= x <= 2.1 for x in ratio), f"ratios {[round(x, 3) for x in ratio]}")
    k10 = q("SELECT count(*) FROM v_coupling_curve_module WHERE curve_id LIKE 'E02%' OR curve_id LIKE '%9oct%'")[0][0]
    b.check("K10", "Module curve view holds no model-error curve (E02) and no superseded curve", k10 == 0, f"{k10} wrong rows")
    over = pd.read_sql("""SELECT curve_id, src_depth_m, spectral_slope, count(*) n, min(tau_s) tau_min, max(tau_s) tau_max, max(eta) eta_max
                          FROM coupling_curve WHERE eta > 1 GROUP BY curve_id, src_depth_m, spectral_slope""", con)
    tot = q("SELECT count(*) FROM coupling_curve")[0][0]
    b.check("K11", "Coupling curve rows above 1 (more acoustic energy than kinetic energy: physically impossible) - listed; such parameter combinations are ruled out by the data",
            "REVIEW" if len(over) else "PASS",
            f"{int(over.n.sum()) if len(over) else 0} of {tot} rows: " + "; ".join(f"{r.curve_id} z={r.src_depth_m:g} m slope {r.spectral_slope:g}: {r.n} rows, tau {r.tau_min:.3g}-{r.tau_max:.3g} s, max {r.eta_max:.3g}" for r in over.itertuples()))
    k12 = q("SELECT value_id, role FROM v_module_chain WHERE role IN ('SUPERSEDED') OR role LIKE 'EXCLUDED%'")
    b.check("K12", "Module-chain view rows whose role is SUPERSEDED or EXCLUDED while status is EVIDENCE - listed for the coupling thread (package data, not edited here)",
            "REVIEW" if k12 else "PASS", "; ".join(f"{v} ({r})" for v, r in k12) or "none")
    b.check("K07", "Coupling inputs match MANIFEST.tsv SHA-256", all(ok for _, ok in man_ok), str(man_ok))
    rv = q("SELECT value FROM noise_estimate WHERE input_file='COUPLING:db_received_observation.csv' LIMIT 1")
    ro0 = float(RO.median_1sRMS_Pa.iloc[0])
    b.check("N09", "Pa to dB conversion of the raw H11 background round-trips (20 log10(p / 1 uPa))", len(rv) == 1 and abs(10 ** (rv[0][0] / 20) * 1e-6 - ro0) < 1e-12,
            f"{ro0} Pa -> {rv[0][0]:.3f} dB re 1 uPa")
    hits = []
    for tbl, idc, cols in [("coupling_value", "value_id", ["read_in_primary", "notes", "source_ref"]),
                           ("coupling_evidence", "evidence_id", ["evidence", "source", "main_error_terms"]),
                           ("impact_case", "case_id", ["hydro_held", "search_status", "notes"]),
                           ("reference_event", "ref_id", ["held_now", "raw_ims_open"]),
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
                                  "Coupling content comes from the coupling thread (session c764a583) package of 25 Oct 2026 via MANIFEST.tsv and is validated by its own validate_coupling_tables.py in every build; F-35A values are points on one curve, no ruling needed (Pete, 24 Oct 2026).",
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
         "**Rules.** Every value carries its definition, unit, source file and SHA-256. Coupling values are used only with the propagation chain "
         "of their definition class (views `v_module_chain`, `v_arons_screen`, `v_envelope`, `v_cross_check`, `v_coupling_curve_module`; rules from the "
         "coupling thread's `validate_coupling_tables.py`, run in every build). The F-35A values are points on "
         "one (coupling, source depth, spectrum) curve from one recording; no ruling is needed (Pete, 24 Oct 2026). Status and defects stay in the registry.", "",
         "## 1. Background noise, median band level by site (dB re 1 uPa^2/Hz unless stated)", ""]
    ns = q("""SELECT site_id, context, band_label, statistic, round(value,1) v, unit, averaging, role FROM noise_estimate
              WHERE statistic='median' ORDER BY context, site_id, band_lo_hz""")
    for (ctx, avg), g in ns.groupby(["context", "averaging"], sort=False):
        piv = g.pivot_table(index="site_id", columns="band_label", values="v", aggfunc="first")
        piv = piv[sorted(piv.columns, key=lambda c: num(c.replace("1/3 octave ", "")))]
        L += [f"**{ctx}; {avg}; unit {g.unit.iloc[0]}; role: {g.role.iloc[0]}**", "", piv.to_markdown(), ""]
    L += ["## 2. Conditions that affect noise", "", q("SELECT site_id, context, condition, effect, source FROM noise_condition").to_markdown(index=False), "",
          "## 3. Coupling definition classes and the propagation chains they may be used with", "",
          q("SELECT definition_class, group_concat(allowed_chain, ', ') AS allowed_chains FROM coupling_definition GROUP BY 1").to_markdown(index=False), "",
          "## 4. Coupling values (coupling thread package, 25 Oct 2026)", "",
          q("""SELECT value_id, evidence_id, quantity, value, value_low, value_high, definition_class, propagation_chain_required AS chain, role, status
               FROM coupling_value""").to_markdown(index=False, floatfmt=".3g"), "",
          "### 4a. Impact families (status PROPOSED_STRUCTURE: awaiting Pete's approval of the structure, not of a number)", "",
          q("SELECT family_id, name, status FROM coupling_family").to_markdown(index=False), "",
          "### 4b. Historical aircraft impact cases", "",
          q("SELECT case_id, event, family, substr(raw_ims_open,1,60) AS raw_ims_open, substr(role,1,60) AS role FROM impact_case").to_markdown(index=False), "",
          "### 4c. Reference events (non-aircraft)", "",
          q("SELECT ref_id, event, substr(used_for,1,60) AS used_for, substr(raw_ims_open,1,40) AS raw_ims_open FROM reference_event").to_markdown(index=False), "",
          "### 4d. Received levels measured from raw records", "",
          q("SELECT obs_id, evidence_id, station, peak_1sRMS_Pa, median_1sRMS_Pa, snr_dB, exposure_Pa2s_30s, band_Hz, date FROM received_observation").to_markdown(index=False), "",
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
