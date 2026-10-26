#!/usr/bin/env python3
"""
build_imports.py - stage 3 of hydro_data.sqlite: data imports declared in imports.yaml (26 Oct 2026).

Pete, 26 Oct 2026: "please pull everything in and instruct all modules and threads to update the repository going forward".
This stage is the repeatable mechanism: a thread adds data by adding ONE block to imports.yaml (path, branch, commit,
SHA-256, kind, target table, units, role, registry id, caveat) and rebuilding. Nobody edits the database by hand.

Run after build_noise_coupling.py (stage 2). It (re)creates only its own tables (listed in table import_block) and
removes only its own rows from shared tables (column import_block), so it can be re-run alone.

Inputs
  --db       hydro_data.sqlite (stages 1-2 built)
  --mod      hydroacoustics module root (branch hypothesis/hydroacoustics); root MOD in imports.yaml
  --work     'Claude Science Project Sep 29' folder of a claude-science-sep29 checkout; root WORK in imports.yaml
  --manifest imports.yaml (default: next to this script)

Checks (I01-I09, one set per block, ids I<nn>_<block>): source SHA-256 equals the manifest; rows in the database equal
rows in the source; a unit is declared for every numeric column; the declared key is unique; coupling rows pass the
package validator on base package plus new rows; updates keep the replaced row in package_row_history.
"""
import argparse, hashlib, importlib.util, io, json, re, shutil, sqlite3, subprocess, sys, tempfile
sys.dont_write_bytecode = True
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, yaml

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STAGE = "imports v1"
HERE = Path(__file__).resolve().parent
# unit by column-name suffix, used when a block says units: auto (an explicit units entry always wins)
SUFFIX_UNITS = [("_utc", "UTC (ISO 8601 text)"), ("_km", "km"), ("_deg", "deg"), ("_m", "m"), ("_s", "s"), ("_hz", "Hz"), ("_Hz", "Hz"),
                ("_db", "dB"), ("_dB", "dB"), ("_pa", "Pa"), ("_Pa", "Pa"), ("_j", "J"), ("_J", "J"), ("_kg", "kg")]
RSTAT = {}   # module registry id -> status (REGISTRY.json)
NAME_UNITS = {"lat": "deg", "lon": "deg", "mag": "magnitude", "size": "magnitude or size as stated in column database"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def resolve(spec, roots):
    root, _, rel = spec.partition(":")
    return Path(roots[root]) / rel


def unit_for(col, units):
    if isinstance(units, dict) and col in units:
        return units[col]
    if units == "auto" or isinstance(units, dict):
        for suf, u in SUFFIX_UNITS:
            if col.endswith(suf) or col.endswith(suf + "_H01W") or col.endswith(suf + "_H08S"):
                return u
        if col in NAME_UNITS:
            return NAME_UNITS[col]
        m = re.match(r"(dist|seismic_leg|water_leg)_.*", col)
        if m:
            return "km"
        if col.startswith("baz_"):
            return "deg"
    return None


class Build:
    def __init__(self, con):
        self.con, self.checks = con, []

    def ins(self, table, rows):
        if isinstance(rows, dict): rows = [rows]
        if not rows: return
        cols = list(rows[0].keys())
        self.con.executemany(f"INSERT INTO [{table}] ({','.join('[' + c + ']' for c in cols)}) VALUES ({','.join('?' * len(cols))})",
                             [[None if (isinstance(r.get(c), float) and np.isnan(r.get(c))) else r.get(c) for c in cols] for r in rows])

    def check(self, cid, desc, result, detail):
        res = result if isinstance(result, str) else ("PASS" if result else "FAIL")
        self.checks.append((cid, desc, res, str(detail)))
        self.con.execute("DELETE FROM check_log WHERE check_id=?", (cid,))
        self.ins("check_log", dict(check_id=cid, description=desc, result=res, detail=str(detail)[:2000], run_utc=BUILD_UTC))


def add_col(con, table, col, typ="TEXT"):
    cols = [r[1] for r in con.execute(f"PRAGMA table_info([{table}])")]
    if col not in cols:
        con.execute(f"ALTER TABLE [{table}] ADD COLUMN [{col}] {typ}")


def numeric_cols(df):
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True); ap.add_argument("--mod", required=True); ap.add_argument("--work", required=True)
    ap.add_argument("--manifest", default=str(HERE / "imports.yaml"))
    a = ap.parse_args()
    roots = {"MOD": a.mod, "WORK": a.work}
    M = yaml.safe_load(Path(a.manifest).read_text())
    con = sqlite3.connect(a.db); b = Build(con)
    # ---- remove the previous run of this stage
    if con.execute("SELECT count(*) FROM sqlite_master WHERE name='import_block'").fetchone()[0]:
        for (t,) in con.execute("SELECT DISTINCT target_table FROM import_table").fetchall():
            con.execute(f"DROP TABLE IF EXISTS [{t}]")
        for tbl in ["noise_estimate", "coupling_value", "received_observation", "coupling_evidence", "data_availability_probe", "attribute"]:
            if "import_block" in [r[1] for r in con.execute(f"PRAGMA table_info([{tbl}])")]:
                con.execute(f"DELETE FROM [{tbl}] WHERE import_block IS NOT NULL")
        if con.execute("SELECT count(*) FROM sqlite_master WHERE name='package_row_history'").fetchone()[0]:
            for t, keyj, rowj in con.execute("SELECT table_name, key_json, old_row_json FROM package_row_history").fetchall():
                key, old = json.loads(keyj), json.loads(rowj)
                con.execute(f"DELETE FROM [{t}] WHERE " + " AND ".join(f"[{k}]=?" for k in key), list(key.values()))
                cols = list(old)
                con.execute(f"INSERT INTO [{t}] ({','.join('[' + c + ']' for c in cols)}) VALUES ({','.join('?' * len(cols))})", [old[c] for c in cols])
        con.execute("DELETE FROM imported_table WHERE table_name IN (SELECT target_table FROM import_table)")
        con.execute("DELETE FROM attribute_key WHERE key LIKE 'array_calibration_%'")
    for t in ["import_block", "import_table", "import_not_imported", "package_row_history", "import_erratum"]:
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute("DELETE FROM check_log WHERE check_id LIKE 'I%'")
    con.executescript("""
    CREATE TABLE import_block (block_id TEXT PRIMARY KEY, kind TEXT, source_path TEXT, branch TEXT, git_commit TEXT, sha256_manifest TEXT,
      sha256_file TEXT, registry_entry_id TEXT, role TEXT, caveat TEXT, n_rows_source INTEGER, n_rows_db INTEGER, built_utc TEXT);
    CREATE TABLE import_table (target_table TEXT PRIMARY KEY, block_id TEXT, source_path TEXT, units_json TEXT, key_json TEXT);
    CREATE TABLE import_not_imported (source_path TEXT, sha256 TEXT, reason TEXT);
    CREATE TABLE package_row_history (table_name TEXT, key_json TEXT, old_row_json TEXT, new_row_json TEXT, block_id TEXT, source_path TEXT, replaced_utc TEXT);
    CREATE TABLE import_erratum (block_id TEXT, erratum_no INTEGER, erratum_text TEXT, affected_table TEXT, affected_ids TEXT, how_applied TEXT);
    """)
    sites = {r[0] for r in con.execute("SELECT site_id FROM site")}
    reg = json.loads((Path(a.mod) / "registry" / "REGISTRY.json").read_text())
    ents = reg["entries"] if isinstance(reg["entries"], list) else list(reg["entries"].values())
    RSTAT.update({e["id"]: e["status"] for e in ents})
    for blk in M["blocks"]:
        bid, kind = blk["id"], blk["kind"]
        tag = re.sub(r"^imp_", "", bid)[:40]
        if kind in ("table", "noise_percentiles", "array_calibration"):
            p = resolve(blk["path"], roots); h = sha(p)
            b.check(f"I01_{tag}", f"{bid}: source SHA-256 equals imports.yaml", h == blk["sha256"], f"{blk['path']} {h[:16]}")
            if kind == "array_calibration":
                import_array_cal(con, b, blk, p, h, tag, sites)
                continue
            df = pd.read_csv(p)
            t = blk["table"]
            df.to_sql(t, con, index=False)
            units = blk.get("units", "auto")
            nc = numeric_cols(df)
            U = {c: unit_for(c, units) for c in nc}
            missing = [c for c, u in U.items() if u is None]
            b.check(f"I02_{tag}", f"{bid}: rows in table {t} equal rows in the source", con.execute(f"SELECT count(*) FROM [{t}]").fetchone()[0] == len(df), f"{len(df)} rows")
            b.check(f"I03_{tag}", f"{bid}: a unit is declared for every numeric column", not missing, f"{len(nc)} numeric columns; missing: {missing}")
            key = blk.get("key")
            dup = int(df.duplicated(key).sum()) if key else -1
            b.check(f"I04_{tag}", f"{bid}: declared key {key} is unique", dup == 0, f"{dup} duplicate keys")
            b.ins("import_table", dict(target_table=t, block_id=bid, source_path=blk["path"], units_json=json.dumps(U), key_json=json.dumps(key)))
            b.ins("imported_table", dict(table_name=t, source_file=blk["path"], sha256=h, n_rows=len(df), n_cols=df.shape[1],
                                         header_comment=f"stage 3 import block {bid}: {blk['role']}", dataset_id=None))
            n_db = len(df)
            if kind == "noise_percentiles":
                n_db = import_noise(con, b, blk, df, h, tag, sites)
            b.ins("import_block", dict(block_id=bid, kind=kind, source_path=blk["path"], branch=blk["branch"], git_commit=blk["commit"], sha256_manifest=blk["sha256"],
                                       sha256_file=h, registry_entry_id=blk["registry_id"], role=blk["role"], caveat=blk["caveat"], n_rows_source=len(df), n_rows_db=n_db, built_utc=BUILD_UTC))
        elif kind == "table_concat":
            parts, hs = [], []
            for spec, hm in zip(blk["paths"], blk["sha256"]):
                p = resolve(spec, roots); h = sha(p); hs.append(h == hm)
                d = pd.read_csv(p); d["source_file"] = spec; parts.append(d)
            df = pd.concat(parts, ignore_index=True); t = blk["table"]
            df.to_sql(t, con, index=False)
            b.check(f"I01_{tag}", f"{bid}: every source SHA-256 equals imports.yaml", all(hs), f"{sum(hs)} of {len(hs)} files")
            b.check(f"I02_{tag}", f"{bid}: rows in table {t} equal rows in the sources", con.execute(f"SELECT count(*) FROM [{t}]").fetchone()[0] == len(df), f"{len(df)} rows")
            U = {c: unit_for(c, blk.get("units", "auto")) for c in numeric_cols(df)}
            missing = [c for c, u in U.items() if u is None]
            b.check(f"I03_{tag}", f"{bid}: a unit is declared for every numeric column", not missing, f"missing: {missing}")
            dup = int(df.duplicated(blk["key"]).sum())
            b.check(f"I04_{tag}", f"{bid}: declared key {blk['key']} is unique", dup == 0, f"{dup} duplicate keys")
            b.ins("import_table", dict(target_table=t, block_id=bid, source_path=";".join(blk["paths"]), units_json=json.dumps(U), key_json=json.dumps(blk["key"])))
            b.ins("imported_table", dict(table_name=t, source_file=";".join(blk["paths"]), sha256=";".join(blk["sha256"]), n_rows=len(df), n_cols=df.shape[1],
                                         header_comment=f"stage 3 import block {bid}: {blk['role']}", dataset_id=None))
            b.ins("import_block", dict(block_id=bid, kind=kind, source_path=";".join(blk["paths"]), branch=blk["branch"], git_commit=blk["commit"],
                                       sha256_manifest=";".join(blk["sha256"]), sha256_file=";".join(blk["sha256"]) if all(hs) else "MISMATCH",
                                       registry_entry_id=blk["registry_id"], role=blk["role"], caveat=blk["caveat"], n_rows_source=len(df), n_rows_db=len(df), built_utc=BUILD_UTC))
        elif kind == "coupling_package_append":
            import_coupling(con, b, blk, roots, tag)
        else:
            b.check(f"I00_{tag}", f"{bid}: known block kind", False, kind)
    for d in M.get("not_imported", []):
        p = resolve(d["path"], roots); h = sha(p)
        b.ins("import_not_imported", dict(source_path=d["path"], sha256=h, reason=d["reason"]))
        b.check(f"I09_{Path(d['path']).stem[:30]}", f"not imported by design: {Path(d['path']).name} (duplicate of an existing table)", h == d["sha256"], d["reason"])
    # stage-wide checks
    ids = [r[0] for r in con.execute("SELECT block_id FROM import_block")]
    b.check("I90", "Every block in imports.yaml has one import_block row", sorted(ids) == sorted(x["id"] for x in M["blocks"]), f"{len(ids)} of {len(M['blocks'])}")
    bad_s = [r[0] for r in con.execute("SELECT DISTINCT site_id FROM noise_estimate WHERE import_block IS NOT NULL") if r[0] not in sites]
    b.check("I91", "Every imported noise row names a site in table site", not bad_s, f"unknown: {bad_s}")
    con.execute("DELETE FROM meta WHERE key LIKE 'stage3_%'")
    for k, v in dict(stage3_schema=STAGE, stage3_built_utc=BUILD_UTC, stage3_manifest_sha256=sha(a.manifest),
                     stage3_scope="Data imports declared in imports.yaml; one block per source file; checks I01-I09 per block, I90-I91 stage-wide.").items():
        b.ins("meta", dict(key=k, value=v))
    con.commit(); con.close()
    for c in b.checks:
        print(f"{c[0]} {c[2]:6s} {c[1]} | {c[3][:140]}")
    if any(c[2] == "FAIL" for c in b.checks):
        sys.exit(1)


def import_noise(con, b, blk, df, h, tag, sites):
    """one noise_estimate row per percentile column; original value, unit and field kept."""
    nz = blk["noise"]; add_col(con, "noise_estimate", "import_block")
    QM, SM = nz["quantity_map"], nz["stat_map"]
    units = dict(con.execute("SELECT quantity_id, unit FROM quantity_def").fetchall())
    rows = []
    sel = df[df.quantity.isin(nz.get("quantities_to_noise_estimate", list(QM)))]
    for r in sel.itertuples(index=False):
        q, btype = QM[r.quantity]
        f = float(r.freq_hz)
        if btype == "1 Hz bin":
            lo, hi, lab = f - 0.5, f + 0.5, f"1 Hz bin {f:g} Hz"
        elif btype == "1/3 octave":
            lo, hi, lab = round(f * 2 ** (-1 / 6), 3), round(f * 2 ** (1 / 6), 3), f"1/3 octave {f:g} Hz"
        else:
            lo, hi, lab = 5.0, 40.0, "5-40 Hz"
        for col, stat in SM.items():
            rows.append(dict(site_id=r.station, sensor_or_element=r.element, context=nz["context"], period_start_utc=None, period_end_utc=None,
                             period_note=f"{r.source} / {r.subset}: March 2015-2019, {r.n_minutes} element-minutes", band_lo_hz=lo, band_hi_hz=hi, band_label=lab,
                             quantity_id=q, statistic=stat, value=float(getattr(r, col)), unit=units[q], original_value=float(getattr(r, col)),
                             original_unit=r.quantity, original_field=col, averaging=nz["averaging"], n_items=int(r.n_minutes), method=nz["method"],
                             source_id=nz["source_id"], dataset_id=None, segment_file=None, input_file=blk["path"], input_sha256=h,
                             registry_entry_id=blk["registry_id"], registry_status=RSTAT.get(blk["registry_id"], "UNKNOWN_ID"), role=blk["role"], caveat=blk["caveat"], import_block=blk["id"]))
    b.ins("noise_estimate", rows)
    n = con.execute("SELECT count(*) FROM noise_estimate WHERE import_block=?", (blk["id"],)).fetchone()[0]
    b.check(f"I05_{tag}", f"{blk['id']}: noise rows equal selected source rows x {len(SM)} statistics", n == len(sel) * len(SM),
            f"{n} rows from {len(sel)} x {len(SM)} (quantities {sorted(sel.quantity.unique())}; all {len(df)} rows in table {blk['table']})")
    # round trip of every value
    db = pd.read_sql("SELECT sensor_or_element e, band_label, period_note, original_unit q, original_field f, value FROM noise_estimate WHERE import_block=?", con, params=(blk["id"],))
    src = sum(float(sel[c].sum()) for c in SM); dbs = float(db.value.sum())
    b.check(f"I06_{tag}", f"{blk['id']}: sum of imported values equals sum of source percentiles (round trip)", abs(src - dbs) < 1e-6 * abs(src), f"source {src:.6f}, db {dbs:.6f}")
    if con.execute("SELECT count(*) FROM source WHERE source_id=?", (nz["source_id"],)).fetchone()[0] == 0:
        b.ins("source", dict(source_id=nz["source_id"], short_name="EarthScope FDSN, IMS hydrophones (open from 2015)", citation="IRIS/EarthScope FDSN dataselect, network IM, channel EDH",
                             year=None, doi_or_url="https://service.earthscope.org/fdsnws/dataselect/1/", local_copy=None, notes="added by build_imports.py (stage 3)"))
    return n


def import_array_cal(con, b, blk, p, h, tag, sites):
    J = json.loads(Path(p).read_text())
    add_col(con, "attribute", "import_block")
    par, ev, att = [], [], []
    U = blk["units"]
    for st, d in J.items():
        for k, v in d["params"].items():
            par.append(dict(station=st, iteration=d["iteration"], n_events=d["n_events"], parameter=k, value=float(v), unit=U[k], source_field=f"{st}.params.{k}"))
        for k in ["raw_residual_median_deg", "raw_residual_robust_sd_deg", "loo_residual_median_deg", "loo_residual_robust_sd_deg", "loo_residual_max_abs_deg"]:
            par.append(dict(station=st, iteration=d["iteration"], n_events=d["n_events"], parameter=k, value=float(d[k]), unit="deg", source_field=f"{st}.{k}"))
        for e in d["events"]:
            ev.append(dict(station=st, cat_evid=str(e[0]), cat_place=e[1], baz_true_deg=e[2], baz_raw_deg=e[3], res_deg=e[4]))
        for k in ["raw_residual_median_deg", "loo_residual_median_deg", "loo_residual_robust_sd_deg"]:
            att.append(dict(entity_type="site", entity_id=st, key=f"array_calibration_{k}", value_num=float(d[k]), unit="deg"))
    pd.DataFrame(par).to_sql("array_calibration", con, index=False)
    pd.DataFrame(ev).to_sql("array_calibration_event", con, index=False)
    acols = [r[1] for r in con.execute("PRAGMA table_info(attribute)")]
    kcols = [r[1] for r in con.execute("PRAGMA table_info(attribute_key)")]
    for x in att:
        kk = dict(key=x["key"], entity_type="site", datatype="real", unit="deg",
                  description="H01W empirical array calibration (41 catalogue T-phases; res = (baz - baz_true + 180) % 360 - 180, analyse.py of ims-march-scripts.zip)")
        b.ins("attribute_key", {c: kk[c] for c in kk if c in kcols})
        row = dict(entity_type="site", entity_id=x["entity_id"], key=x["key"], value_num=x["value_num"], unit="deg", source_id=None, evidence="imported",
                   note=f"{blk['path']} (sha256 {h[:16]})", added_utc=BUILD_UTC, import_block=blk["id"])
        b.ins("attribute", {c: row[c] for c in row if c in acols})
    n_ev = sum(len(d["events"]) for d in J.values())
    b.check(f"I02_{tag}", f"{blk['id']}: event rows equal the JSON event list; parameter rows equal 7 + 5 per station",
            con.execute("SELECT count(*) FROM array_calibration_event").fetchone()[0] == n_ev and len(par) == 12 * len(J), f"{n_ev} events, {len(par)} parameters")
    missing = [k for k in J[next(iter(J))]["params"] if k not in U]
    b.check(f"I03_{tag}", f"{blk['id']}: a unit is declared for every parameter", not missing, f"missing: {missing}")
    dup = int(pd.DataFrame(ev).duplicated(["station", "cat_evid"]).sum())
    b.check(f"I04_{tag}", f"{blk['id']}: event ids unique per station", dup == 0, f"{dup} duplicates")
    b.check(f"I05_{tag}", f"{blk['id']}: calibration station exists in table site", all(s in sites for s in J), list(J))
    for t in ["array_calibration", "array_calibration_event"]:
        b.ins("import_table", dict(target_table=t, block_id=blk["id"], source_path=blk["path"], units_json=json.dumps(U), key_json=None))
        b.ins("imported_table", dict(table_name=t, source_file=blk["path"], sha256=h, n_rows=con.execute(f"SELECT count(*) FROM [{t}]").fetchone()[0], n_cols=None,
                                     header_comment=f"stage 3 import block {blk['id']}: {blk['role']}", dataset_id=None))
    b.ins("import_block", dict(block_id=blk["id"], kind=blk["kind"], source_path=blk["path"], branch=blk["branch"], git_commit=blk["commit"], sha256_manifest=blk["sha256"],
                               sha256_file=h, registry_entry_id=blk["registry_id"], role=blk["role"], caveat=blk["caveat"], n_rows_source=n_ev, n_rows_db=n_ev, built_utc=BUILD_UTC))


ERRATA_APPLY = {   # verifier errata in raw-data-2026-10-25/README.md: how each one reaches the database (values never changed)
    1: ("coupling_value", None, "applied by the producer before the merge (wording of 31 cells); checked: no cell holds 'one-pole f^-2'"),
    2: (None, None, "no database row holds the Kadri replication offsets (string search for -742 and -1,594: none)"),
    3: (None, None, "no database row holds the AB Aviation 1103 expected bearing 254.56 (string search: none)"),
    4: (None, None, "no database row holds the triad exposures 0.284 / 0.0955 or the 4-40 Hz peak ranges (string search: none); OB64-OB69 are per-element 4-64 Hz values"),
    5: ("received_observation", "station = 'H10S1' AND method LIKE 'sj_charge%'", "column erratum set on the row: noise maximum, not an arrival; -27 dB is a lower bound on the H10S1 deficit"),
    6: (None, None, "wording of the propagation note only (no database row)"),
    7: ("impact_case", "case_id = 'AC05'", "column erratum set on the row: the H11N-H11S lags are 73.3 s and 71.5 s for the two pulses (the notes say 72-73 s)"),
}


def import_coupling(con, b, blk, roots, tag):
    """append wave-3 rows to the package tables after the package's own validator passes on base + new rows."""
    cdir = HERE / "inputs" / "coupling"
    tmp = Path(tempfile.mkdtemp(prefix="cpl_"))
    for f in cdir.glob("*"):
        shutil.copy(f, tmp / f.name)
    _sp = importlib.util.spec_from_file_location("vct", cdir / "validate_coupling_tables.py"); V = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V)
    fmap = {"coupling_value": "coupling_value", "received_observation": "received_observation", "coupling_evidence": "coupling_evidence",
            "data_availability_probe": "data_availability_probe", "impact_case": "impact_case", "coupling_family_element_evidence": "family_element_evidence"}
    new, upd, hs, n_src = {}, {}, [], 0
    for item in blk["append"] + blk["update"]:
        p = resolve(item["file"], roots); h = sha(p); hs.append((item["file"], h == item["sha256"]))
        d = pd.read_csv(p); d["input_file"] = item["file"]; d["input_sha256"] = h; d["import_block"] = blk["id"]
        n_src += len(d)
        (new if item in blk["append"] else upd)[item["table"]] = (d, item)
    b.check(f"I01_{tag}", f"{blk['id']}: every source SHA-256 equals imports.yaml", all(ok for _, ok in hs), str([(Path(f).name, ok) for f, ok in hs]))
    # merged package in a temp folder: base + appended rows, updated rows replaced
    for t, (d, item) in list(new.items()) + list(upd.items()):
        f = tmp / V.FILES[fmap[t]]
        base = pd.read_csv(f)
        keep = d[[c for c in base.columns if c in d.columns]]
        if t in upd:
            key = item["key"]
            m = base.set_index(key).index.isin(keep.set_index(key).index)
            base = base[~m]
        pd.concat([base, keep], ignore_index=True).to_csv(f, index=False)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = V.main(str(tmp))
    out = buf.getvalue()
    b.check(f"I05_{tag}", f"{blk['id']}: coupling package validator (validate_coupling_tables.py, 25 Oct 2026) passes on base package plus wave-3 rows",
            rc == 0 and "RESULT: PASS" in out, "; ".join(l.strip() for l in out.splitlines() if l.startswith(("FAIL", "RESULT", "  v_")))[:900])
    if rc != 0:
        return
    # append
    for t, (d, item) in new.items():
        for c in d.columns:
            add_col(con, t, c)
        cols = [r[1] for r in con.execute(f"PRAGMA table_info([{t}])")]
        b.ins(t, [{c: (None if pd.isna(v) else (v.item() if hasattr(v, "item") else v)) for c, v in r.items() if c in cols} for r in d.to_dict("records")])
        n_db = con.execute(f"SELECT count(*) FROM [{t}] WHERE import_block=?", (blk["id"],)).fetchone()[0]
        key = item["key"]; keys = key if isinstance(key, list) else [key]
        kq = ",".join(f"[{k}]" for k in keys)
        dup = con.execute(f"SELECT count(*) FROM (SELECT {kq}, count(*) n FROM [{t}] GROUP BY {kq} HAVING n > 1)").fetchone()[0]
        rng = ""
        if "expect_ids" in item and "-" in item["expect_ids"]:
            lo, hi = item["expect_ids"].split("-"); pre = re.match(r"[A-Z]+", lo).group(0)
            want = {f"{pre}{i:02d}" for i in range(int(lo[len(pre):]), int(hi[len(pre):]) + 1)}
            rng = f"; ids {item['expect_ids']} complete: {set(d[key]) == want}"
            dup += 0 if set(d[key]) == want else 1
        b.check(f"I06_{tag}_{t}"[:60], f"{blk['id']}: {t}: rows added equal source rows; ids unique in the table after the append", n_db == len(d) and dup == 0,
                f"{n_db} of {len(d)} rows; {dup} duplicate keys{rng}")
    # updates, old row kept in package_row_history
    for t, (d, item) in upd.items():
        for c in ["input_file", "input_sha256", "import_block", "erratum"]:
            add_col(con, t, c)
        cols = [r[1] for r in con.execute(f"PRAGMA table_info([{t}])")]
        for r in d.to_dict("records"):
            key = {k: r[k] for k in item["key"]}
            where = " AND ".join(f"[{k}]=?" for k in key)
            old = pd.read_sql(f"SELECT * FROM [{t}] WHERE {where}", con, params=list(key.values()))
            new_row = {c: (None if pd.isna(v) else v) for c, v in r.items() if c in cols}
            b.ins("package_row_history", dict(table_name=t, key_json=json.dumps(key), old_row_json=old.iloc[0].to_json() if len(old) else "{}",
                                              new_row_json=json.dumps(new_row, default=str), block_id=blk["id"], source_path=item["file"], replaced_utc=BUILD_UTC))
            con.execute(f"DELETE FROM [{t}] WHERE {where}", list(key.values()))
            b.ins(t, new_row)
        nh = con.execute("SELECT count(*) FROM package_row_history WHERE table_name=?", (t,)).fetchone()[0]
        b.check(f"I07_{tag}_{t}"[:60], f"{blk['id']}: {t}: each update replaced one row and kept the old row in package_row_history", nh == len(d), f"{nh} of {len(d)}")
    # errata
    for t in ["received_observation", "impact_case"]:
        add_col(con, t, "erratum")
    txt = resolve(blk["errata"], roots).read_text()
    sec = txt.split("## Errata found by the verifier", 1)[1].split("\n## ", 1)[0]
    items = re.findall(r"^(\d)\. (.+?)(?=^\d\. |\Z)", sec, flags=re.S | re.M)
    b.check(f"I08_{tag}", f"{blk['id']}: errata source SHA-256 equals imports.yaml and holds 7 errata", sha(resolve(blk["errata"], roots)) == blk["errata_sha256"] and len(items) == 7, f"{len(items)} errata")
    for no, body in items:
        no = int(no); t, where, how = ERRATA_APPLY[no]; ids = ""
        if t and where:
            idc = "obs_id" if t == "received_observation" else "case_id"
            ids = ",".join(r[0] for r in con.execute(f"SELECT {idc} FROM [{t}] WHERE {where}"))
            con.execute(f"UPDATE [{t}] SET erratum=? WHERE {where}", (f"verifier erratum {no} (raw-data-2026-10-25/README.md): {how.split(': ', 1)[-1]}",))
        b.ins("import_erratum", dict(block_id=blk["id"], erratum_no=no, erratum_text=" ".join(body.split()), affected_table=t, affected_ids=ids, how_applied=how))
    W1 = "(notes LIKE '%one-pole f^-2%' OR quantity LIKE '%one-pole f^-2%' OR numerator LIKE '%one-pole f^-2%')"
    n_one = con.execute(f"SELECT count(*) FROM coupling_value WHERE import_block=? AND {W1}", (blk["id"],)).fetchone()[0]
    b.check(f"I08b_{tag}", f"{blk['id']}: erratum 1 holds in the wave-3 rows (no cell says 'one-pole f^-2')", n_one == 0, f"{n_one} cells")
    base1 = [r[0] for r in con.execute(f"SELECT value_id FROM coupling_value WHERE import_block IS NULL AND {W1}")]
    b.check(f"I08c_{tag}", "Base package rows (stage 2) that still use the 'one-pole f^-2' wording of erratum 1 - listed for the coupling thread; "
            "the base package is not edited here", "REVIEW" if base1 else "PASS", ", ".join(base1) or "none")
    b.ins("import_block", dict(block_id=blk["id"], kind=blk["kind"], source_path=";".join(i["file"] for i in blk["append"] + blk["update"]), branch=blk["branch"],
                               git_commit=blk["commit"], sha256_manifest=";".join(i["sha256"] for i in blk["append"] + blk["update"]),
                               sha256_file="match" if all(ok for _, ok in hs) else "MISMATCH", registry_entry_id=blk["registry_id"], role=blk["role"],
                               caveat=blk["caveat"], n_rows_source=n_src, n_rows_db=n_src, built_utc=BUILD_UTC))
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
