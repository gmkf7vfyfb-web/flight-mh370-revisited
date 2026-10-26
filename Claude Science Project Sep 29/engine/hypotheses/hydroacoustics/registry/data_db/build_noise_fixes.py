#!/usr/bin/env python3
"""
build_noise_fixes.py - stage 4 of hydro_data.sqlite: fixes of three noise caveats (C1-C3), 26 Oct 2026.

Pete, 26 Oct 2026: "(3) please check on and fix the items noted in caveats". Pre-registration (with amendment 1):
results/hydroacoustics/noise-caveat-fixes-2026-10-26/PREREGISTRATION.md on claude-science-sep29. This stage adds rows; it
deletes no earlier row. Run after build_imports.py (stage 3). It re-creates only its own tables and its own noise rows
(noise_estimate.import_block LIKE 'fix_C%'), and re-creates the views v_noise_summary and v_noise_8mar2014 with two
extra columns: preferred_8mar2014 and preference_reason (Pete's instruction, 26 Oct 2026, via the coordinating session).

C1  8 Mar 2014 H01W and H08S 5-40 Hz levels from the digitised Kadri 2024 Fig. 9 pressure traces (1-s peak-to-peak of the
    vertices / k; k measured on raw IMS records by prepare/noise_caveat_calibration.py).
C2  IMOS logger gain: result of prepare/noise_caveat_imos_gain_check.py and the quoted code lines (no correction needed
    if the per-bin recompute equals the module file).
C3  (i) IMOS 3315 against CMST 2014 Fig. 1 (absolute level); (ii) one table of H01W/H08S 5-40 Hz levels from every held
    source; (iii) OHASISBIO SSEIR and SWAMS3 by transfer calibration via H01W2 (Royer 2016 spectrograms).

Inputs: --db hydro_data.sqlite, --mod module root (reads results-data/noise-caveat-fixes-2026-10-26/ and prepare/imos_noise.py).
"""
import argparse, hashlib, json, re, sqlite3, sys
sys.dont_write_bytecode = True
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STAGE = "noise-fixes v1"
RUN = "noise-caveat-fixes-2026-10-26"
REG = "res.noise_caveat_fixes_2026_10_26"
SEED, NBOOT, BLOCK_S = 20261026, 2000, 30
BW_5_40 = 10 * np.log10(35.0)
PANELS = {"a": ("H01W", "2014-03-08T00:27:00Z", "2014-03-08T00:37:00Z"), "b": ("H01W", "2014-03-08T00:37:00Z", "2014-03-08T00:47:00Z"),
          "c": ("H01W", "2014-03-08T00:47:00Z", "2014-03-08T00:57:00Z"), "d": ("H08S", "2014-03-08T01:00:00Z", "2014-03-08T01:10:00Z"),
          "e": ("H08S", "2014-03-08T01:10:00Z", "2014-03-08T01:20:00Z")}
ROYER_CAVEAT = "Royer 2016 reports that powerful seismic-survey shots obscured much of the OHASISBIO data that day."


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def db20(p_pa):
    return 20 * np.log10(np.asarray(p_pa) / 1e-6)


class Build:
    def __init__(self, con): self.con, self.checks = con, []

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
    if col not in [r[1] for r in con.execute(f"PRAGMA table_info([{table}])")]:
        con.execute(f"ALTER TABLE [{table}] ADD COLUMN [{col}] {typ}")


def per_second(con, panel):
    st = PANELS[panel][0].lower()
    d = pd.read_sql(f"SELECT utc, pressure_pa FROM dg_data_kadri_fig9_digitised_kadri_2024_figure9_panel_{panel}_{st}", con)
    t = pd.to_datetime(d.utc, utc=True)
    t0 = pd.Timestamp(PANELS[panel][1])
    sec = np.floor((t - t0).dt.total_seconds().values).astype(int)
    g = pd.DataFrame(dict(sec=sec, x=d.pressure_pa.values)).groupby("sec").x
    r = pd.DataFrame(dict(pp=g.max() - g.min(), n=g.size(), vms=g.apply(lambda v: float(np.mean(v ** 2)))))
    r["t_utc"] = [t0 + pd.Timedelta(seconds=int(s)) for s in r.index]
    return r, d


def exclude(r, times, before, after):
    ex = np.zeros(len(r), bool)
    s0 = r.index.values.astype(float); s1 = s0 + 1
    t0 = r.t_utc.iloc[0] - pd.Timedelta(seconds=int(r.index[0]))
    for te in times:
        s = (pd.Timestamp(te) - t0).total_seconds()
        ex |= (s1 > s - before) & (s0 < s + after)
    return ex


def block_boot_median(levels, secs, rng):
    blk = (np.asarray(secs) // BLOCK_S).astype(int)
    ub = np.unique(blk); groups = [levels[blk == u] for u in ub]
    meds = np.empty(NBOOT)
    for i in range(NBOOT):
        pick = rng.integers(0, len(groups), len(groups))
        meds[i] = np.median(np.concatenate([groups[j] for j in pick]))
    return float(np.std(meds, ddof=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--db", required=True); ap.add_argument("--mod", required=True)
    a = ap.parse_args(); mod = Path(a.mod); rd = mod / "results-data" / RUN
    con = sqlite3.connect(a.db); b = Build(con); rng = np.random.default_rng(SEED)
    reg = json.loads((mod / "registry" / "REGISTRY.json").read_text())
    ents = reg["entries"] if isinstance(reg["entries"], list) else list(reg["entries"].values())
    RSTATUS = {e["id"]: e["status"] for e in ents}.get(REG, "UNREGISTERED")
    for c in ["import_block", "uncertainty_db", "uncertainty_note"]:
        add_col(con, "noise_estimate", c, "REAL" if c == "uncertainty_db" else "TEXT")
    con.execute("DELETE FROM noise_estimate WHERE import_block LIKE 'fix_C%'")
    for v in ["v_noise_summary", "v_noise_8mar2014", "v_ims_noise_5_40_compare"]:
        con.execute(f"DROP VIEW IF EXISTS {v}")
    for t in ["noise_fix_calibration", "noise_fix_result", "noise_preference", "noise_compare_5_40", "absolute_level_check", "imos_gain_check", "noise_fix_input"]:
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute("DELETE FROM check_log WHERE check_id LIKE 'F%'")
    con.executescript("""
    CREATE TABLE noise_fix_input (item TEXT, file_path TEXT, sha256 TEXT, definition_quote TEXT);
    CREATE TABLE noise_fix_result (item TEXT, site_id TEXT, quantity TEXT, value REAL, unit TEXT, sigma REAL, detail TEXT);
    CREATE TABLE noise_preference (noise_id INTEGER PRIMARY KEY, preferred_8mar2014 INTEGER, preference_reason TEXT, decided_by TEXT);
    CREATE TABLE noise_compare_5_40 (site_id TEXT, source TEXT, year_or_period TEXT, statistic TEXT, spl_5_40_db REAL, sigma_db REAL,
      derivation TEXT, noise_ids TEXT, method TEXT);
    CREATE TABLE absolute_level_check (check_item TEXT, quantity TEXT, measured REAL, published REAL, unit TEXT, diff_db REAL,
      criterion TEXT, result TEXT, source_tables TEXT);
    """)
    q = lambda s, p=(): con.execute(s, p).fetchall()

    def inp(item, rel, quote):
        p = mod / rel; h = sha(p) if p.exists() else "MISSING"
        b.ins("noise_fix_input", dict(item=item, file_path="MOD:" + rel, sha256=h, definition_quote=quote)); return h

    # ------------------------------------------------------------------ C1
    cal_rel = f"results-data/{RUN}/pp_rms_calibration_summary.json"
    h_cal = inp("C1", cal_rel, "k = median over 1-s windows of PP/RMS on raw IMS records, 5-40 Hz (noise_caveat_calibration.py docstring)")
    CAL = json.loads((mod / cal_rel).read_text())["stations"]
    pd.read_csv(rd / "pp_rms_calibration.csv").to_sql("noise_fix_calibration", con, index=False)
    trans = [r[0] for r in q("SELECT t_utc FROM pick WHERE dataset_id='kadri2024_table1'")]
    shots = [r[0] for r in q("SELECT t_utc FROM pick WHERE kind='airgun shot' AND site_id='H08S'")]
    b.check("F01", "C1 inputs: 19 Kadri Table 1 transients and 110 H08S airgun shots in table pick", len(trans) == 19 and len(shots) == 110, f"{len(trans)} transients, {len(shots)} shots")
    per = {}
    for p in "abcde":
        r, d = per_second(con, p); st = PANELS[p][0]
        full = r.n >= 8
        if st == "H01W":
            quiet = full & ~exclude(r, trans, 3.0, 3.0)
        else:
            quiet = full & ~exclude(r, shots, 1.5, 3.5)
        k = CAL[st]["k"]
        with np.errstate(divide="ignore"):
            lev = db20(r.pp.values / k); vr = db20(np.sqrt(r.vms.values) / CAL[st]["vrms_ratio"])
        per[p] = dict(r=r, quiet=quiet.values, full=full.values, lev=lev, k=k, vrms=vr)
    rel_k = {p: f"data/kadri_fig9_digitised/kadri-2024-figure9-panel-{p}-{PANELS[p][0]}.csv" for p in "abcde"}
    hk = {p: inp("C1", rel_k[p], "PDF vector vertices of the plotted waveform; envelope resolution only (dataset kadri2024_fig9_*)") for p in "abcde"}
    c1_rows, c1_res = [], {}

    def c1_row(st, label, panels, sel_key, role, note):
        lv = np.concatenate([per[p]["lev"][per[p][sel_key]] for p in panels])
        sc = np.concatenate([per[p]["r"].index.values[per[p][sel_key]] + 600 * i for i, p in enumerate(panels)])
        vr = np.concatenate([per[p]["vrms"][per[p][sel_key]] for p in panels])
        s_a = block_boot_median(lv, sc, rng); s_b = CAL[st]["k_sigma_db"]; s_c = CAL[st]["plot_rate_sigma_db"]
        sig = float(np.sqrt(s_a ** 2 + s_b ** 2 + s_c ** 2))
        med = float(np.median(lv))
        t0 = PANELS[panels[0]][1]; t1 = PANELS[panels[-1]][2]
        pp_med = float(np.median(np.concatenate([per[p]["r"].pp.values[per[p][sel_key]] for p in panels])))
        unc = f"1 sigma {sig:.2f} dB = sampling {s_a:.2f} (30-s block bootstrap, {NBOOT} draws) + ratio k {s_b:.2f} + plotting rate {s_c:.2f}, in quadrature"
        cav = (f"Digitised PDF vertices of a published trace (Kadri 2024 Fig. 9; element and filter order not stated). RMS = 1-s peak-to-peak / k, "
               f"k = {CAL[st]['k']:.3f} from raw {st} records of 8 March 2015-2019 at the same clock time. Axis scale of the published panel not re-checked. {note}")
        for stat, val in [("median", med), ("p10", float(np.percentile(lv, 10))), ("p90", float(np.percentile(lv, 90)))]:
            c1_rows.append(dict(site_id=st, sensor_or_element=label, context="MH370 8 Mar 2014", period_start_utc=t0, period_end_utc=t1,
                                period_note=f"Kadri 2024 Fig. 9 {label}; {len(lv)} seconds ({sel_key})", band_lo_hz=5.0, band_hi_hz=40.0, band_label="5-40 Hz",
                                quantity_id="rms_level", statistic=stat, value=round(val, 3), unit="dB re 1 uPa", original_value=round(pp_med, 6),
                                original_unit="Pa (median 1-s peak-to-peak of the vertices)", original_field="pressure_pa",
                                averaging="1 s RMS (1-s peak-to-peak / k); statistic over the selected seconds", n_items=int(len(lv)),
                                method="digitised from published pressure trace", source_id="kadri2024", dataset_id=f"kadri2024_fig9_{st.lower()}",
                                segment_file=None, input_file="MOD:" + rel_k[panels[0]] + ("" if len(panels) == 1 else f" (+{len(panels) - 1} panels)"),
                                input_sha256=hk[panels[0]], registry_entry_id=REG, registry_status=RSTATUS, role=role, caveat=cav,
                                import_block="fix_C1", uncertainty_db=round(sig, 3) if stat == "median" else None, uncertainty_note=unc if stat == "median" else None))
        c1_res[(st, label, sel_key)] = dict(median=med, sigma=sig, s_a=s_a, s_b=s_b, s_c=s_c, n=len(lv), vrms_median=float(np.median(vr)))
        b.ins("noise_fix_result", dict(item="C1", site_id=st, quantity=f"5-40 Hz SPL, median 1-s RMS, {label} ({sel_key})", value=round(med, 3), unit="dB re 1 uPa",
                                       sigma=round(sig, 3), detail=f"{unc}; second estimator (vertex RMS / {CAL[st]['vrms_ratio']:.3f}) {np.median(vr):.2f} dB"))
    for p in "abc":
        c1_row("H01W", f"Fig. 9 panel {p}", [p], "quiet", "background (event day, trace)", "Seconds within 3 s of a Kadri Table 1 transient excluded.")
    c1_row("H01W", "Fig. 9 panels a-c", list("abc"), "quiet", "background (event day, trace)", "Seconds within 3 s of a Kadri Table 1 transient excluded.")
    c1_row("H08S", "Fig. 9 panel d", ["d"], "quiet", "background between airgun shots (event day, trace)",
           "Seconds from 1.5 s before to 3.5 s after each airgun shot (table pick) excluded.")
    c1_row("H08S", "Fig. 9 panel d", ["d"], "full", "context: all seconds, airgun shots included (event day, trace)", "Airgun shots included.")
    c1_row("H08S", "Fig. 9 panel e", ["e"], "quiet", "sensitivity only: panel e (event day, trace)",
           "Panel e has a +8.8 dB amplitude step at the panel join (dataset caveat); not pooled.")
    b.ins("noise_estimate", c1_rows)
    h1 = c1_res[("H01W", "Fig. 9 panels a-c", "quiet")]; h8 = c1_res[("H08S", "Fig. 9 panel d", "quiet")]
    b.check("F02", "C1 H01W trace level (panels a-c, quiet seconds) compared with the expected order 102-103 dB (task); |difference| > 2 dB is reported, not failed",
            "PASS" if 100.0 <= h1["median"] <= 105.0 else "REVIEW", f"{h1['median']:.2f} +/- {h1['sigma']:.2f} dB re 1 uPa (n={h1['n']} s); second estimator {h1['vrms_median']:.2f} dB")
    pa = [c1_res[("H01W", f"Fig. 9 panel {p}", "quiet")]["median"] for p in "abc"]
    b.check("F03", "C1 panel-to-panel consistency at H01W (axis-scale check): range of the three panel medians <= 2 dB", max(pa) - min(pa) <= 2.0,
            f"panels a/b/c {pa[0]:.2f} / {pa[1]:.2f} / {pa[2]:.2f} dB")
    b.check("F04", "C1 second estimator (vertex RMS / min-max decimation ratio) within 2 dB of the peak-to-peak estimator, H01W and H08S panel d",
            abs(h1["vrms_median"] - h1["median"]) <= 2 and abs(h8["vrms_median"] - h8["median"]) <= 2,
            f"H01W {h1['vrms_median']:.2f} vs {h1['median']:.2f}; H08S {h8['vrms_median']:.2f} vs {h8['median']:.2f}")
    # preference marks (Pete's instruction, 26 Oct 2026): which 8 Mar 2014 row is preferred and why
    ids = {r[1]: r[0] for r in q("SELECT noise_id, site_id || '|' || sensor_or_element || '|' || role FROM noise_estimate WHERE import_block='fix_C1' AND statistic='median'")}
    pref = []
    for nid, site, src, meth, role in q("SELECT noise_id, site_id, source_id, method, role FROM noise_estimate WHERE context='MH370 8 Mar 2014' AND site_id IN ('H01W','H08S')"):
        if src == "kadri2024" and meth.startswith("digitised from published spectrogram"):
            pref.append(dict(noise_id=nid, preferred_8mar2014=0, preference_reason=(
                "Not preferred: spectrogram-colour reading; its own caveat says biased low (64 dB colour floor, JPEG darkening). "
                if site == "H01W" else "Not preferred: spectrogram-colour reading (colour floor and JPEG effects as at H01W). ") +
                f"Preferred row: trace-based 1-s RMS from the same figure (noise_id {ids.get('H01W|Fig. 9 panels a-c|background (event day, trace)') if site == 'H01W' else ids.get('H08S|Fig. 9 panel d|background between airgun shots (event day, trace)')}).",
                decided_by="Pete's instruction 26 Oct 2026 (fix C1); reason from the existing caveat"))
    allc1 = q("SELECT noise_id, site_id || '|' || sensor_or_element || '|' || role FROM noise_estimate WHERE import_block='fix_C1'")
    for nid, key in allc1:
        site, lab, role = key.split("|")
        if lab in ("Fig. 9 panels a-c",) or (site == "H08S" and lab == "Fig. 9 panel d" and role.startswith("background between")):
            pref.append(dict(noise_id=nid, preferred_8mar2014=1, preference_reason="Preferred 8 Mar 2014 level: measured from the published pressure trace, "
                             "the ratio k calibrated on raw records of the same station, season and clock time; no colour floor.", decided_by="fix C1, 26 Oct 2026"))
        else:
            pref.append(dict(noise_id=nid, preferred_8mar2014=0, preference_reason="Not preferred: single panel, context row or sensitivity row; the pooled trace row is preferred.",
                             decided_by="fix C1, 26 Oct 2026"))
    b.ins("noise_preference", pref)

    # ------------------------------------------------------------------ C2
    gq = Path(mod / "prepare/imos_noise.py").read_text().splitlines()
    want = ['cal = 10 ** ((Gi(f) + L["sens_db"]) / 10)', 'pu = p / cal', 'p1u = p1 / (10 ** ((Gi(f1) + L["sens_db"]) / 10))']
    found = [(i + 1, l.strip()) for i, l in enumerate(gq) if any(w in l for w in want)]
    inp("C2", "prepare/imos_noise.py", " | ".join(f"line {n}: {t}" for n, t in found))
    ncq = Path(mod / "registry/data_db/build_noise_coupling.py").read_text().splitlines()
    fnc = [(i + 1, l.strip()) for i, l in enumerate(ncq) if 'value=float(r[bd])' in l or 'value=float(r[fld])' in l]
    inp("C2", "registry/data_db/build_noise_coupling.py", " | ".join(f"line {n}: {t[:120]}" for n, t in fnc))
    G = json.loads((rd / "imos_gain_check.json").read_text()); inp("C2", f"results-data/{RUN}/imos_gain_check.json", "per_bin vs flat100 recompute of IMOS band levels")
    pd.read_csv(rd / "imos_gain_check.csv").to_sql("imos_gain_check", con, index=False)
    b.check("F05", "C2: imos_noise.py applies the logger gain per frequency bin before band averaging (code lines found)", len(found) == 3,
            " | ".join(f"line {n}: {t}" for n, t in found))
    b.check("F06", "C2: per-bin recompute of IMOS band levels equals noise_per_recording.csv within 0.05 dB (pre-registered)", G["pass_per_bin_within_0_05_db"],
            f"{G['n_records']} records x 7 bands, max |diff| {G['per_bin_max_abs_diff_db']} dB; a flat 100 Hz gain would change 10-20 Hz by " +
            ", ".join(f"{k.split()[0]} {v:+.2f}" for k, v in G["flat100_minus_file_by_logger_band"].items() if k.endswith(" 10-20")) + " dB")
    b.check("F07", "C2: build_noise_coupling.py copies the IMOS band values from the module files unchanged (no second gain step)", len(fnc) >= 2,
            " | ".join(f"line {n}" for n, _ in fnc))
    for k, v in G["flat100_minus_file_by_logger_band"].items():
        b.ins("noise_fix_result", dict(item="C2", site_id=f"IMOS{k.split()[0]}", quantity=f"band {k.split()[1]} Hz: level with a flat 100 Hz gain minus the database level",
                                       value=round(v, 3), unit="dB", sigma=None, detail="no correction made: the database levels already include the per-bin gain"))

    # ------------------------------------------------------------------ C3 (i) IMOS 3315 against CMST 2014 Fig. 1
    meas = pd.read_sql("SELECT * FROM dg_waveform_rasters_cmst_fig1_overlay_imos3315_531a728a_1_120hz_column_envelope", con)
    meas540 = pd.read_sql("SELECT * FROM dg_waveform_rasters_cmst_fig1_overlay_imos3315_531a728a_5_40hz_column_envelope", con)
    cm = pd.read_sql("SELECT * FROM dg_waveform_rasters_cmst2014_fig1_perth_canyon_digitised", con)
    def env_stats(t, up, lo):
        e = np.where(np.abs(up) > np.abs(lo), up, lo); w = (t >= 205) & (t <= 245)
        return float(np.abs(e).max()), float(np.percentile(np.abs(e[~w]), 99))
    mp, mn = env_stats(meas.t_s.values, meas.upper_pa.values, meas.lower_pa.values)
    m5p, m5n = env_stats(meas540.t_s.values, meas540.upper_pa.values, meas540.lower_pa.values)
    cp, cn = env_stats(cm.t_s.values, cm.upper.values, cm.lower.values)
    for lab, mv, cv in [("peak |p| (1-120 Hz)", mp, cp), ("p99 of |envelope| outside 205-245 s (1-120 Hz)", mn, cn)]:
        dd = float(20 * np.log10(mv / cv))
        b.ins("absolute_level_check", dict(check_item="C3(i) IMOS 3315 531A728A vs CMST 2014 Fig. 1", quantity=lab, measured=round(mv, 4), published=round(cv, 4), unit="Pa",
                                           diff_db=round(dd, 2), criterion="|diff| <= 2 dB (pre-registered)", result="PASS" if abs(dd) <= 2 else "FAIL",
                                           source_tables="dg_waveform_rasters_cmst_fig1_overlay_imos3315_531a728a_1_120hz_column_envelope; dg_waveform_rasters_cmst2014_fig1_perth_canyon_digitised"))
    for lab, mv, cv in [("peak |p| (5-40 Hz, information only)", m5p, cp), ("p99 outside 205-245 s (5-40 Hz, information only)", m5n, cn)]:
        b.ins("absolute_level_check", dict(check_item="C3(i) IMOS 3315 531A728A vs CMST 2014 Fig. 1", quantity=lab, measured=round(mv, 4), published=round(cv, 4), unit="Pa",
                                           diff_db=round(float(20 * np.log10(mv / cv)), 2), criterion="none (CMST band not stated; information only)", result="INFO",
                                           source_tables="dg_waveform_rasters_cmst_fig1_overlay_imos3315_531a728a_5_40hz_column_envelope; dg_waveform_rasters_cmst2014_fig1_perth_canyon_digitised"))
    d1, d2 = 20 * np.log10(mp / cp), 20 * np.log10(mn / cn)
    b.check("F08", "C3(i) absolute level: IMOS 3315 (module calibration incl. per-bin logger gain, 1-120 Hz) against the digitised CMST 2014 Fig. 1, peak and noise p99 within 2 dB",
            abs(d1) <= 2 and abs(d2) <= 2, f"peak {mp:.3f} vs {cp:.3f} Pa ({d1:+.2f} dB); noise p99 {mn:.3f} vs {cn:.3f} Pa ({d2:+.2f} dB)")

    # ------------------------------------------------------------------ C3 (iii) OHASISBIO transfer via H01W2
    def royer(station, t0, t1):
        tabs = [r[0] for r in q(f"SELECT name FROM sqlite_master WHERE name LIKE 'dg_royer_2016_spectrograms_appendix_{station}_{station}_%_band'")]
        d = pd.concat([pd.read_sql(f"SELECT t_utc_s, psd_db_5_40 FROM [{t}]", con) for t in tabs], ignore_index=True)
        s0 = (pd.Timestamp(t0) - pd.Timestamp("2014-03-08T00:00:00Z")).total_seconds(); s1 = (pd.Timestamp(t1) - pd.Timestamp("2014-03-08T00:00:00Z")).total_seconds()
        return d[(d.t_utc_s >= s0) & (d.t_utc_s < s1)].psd_db_5_40.values, tabs
    offs = []
    for p in "abc":
        rv, _ = royer("h01w2", PANELS[p][1], PANELS[p][2])
        offs.append(c1_res[("H01W", f"Fig. 9 panel {p}", "quiet")]["median"] - (np.median(rv) + BW_5_40))
    rv, tabs_h = royer("h01w2", PANELS["a"][1], PANELS["c"][2])
    royer_h01w_spl = float(np.median(rv) + BW_5_40)
    offset = h1["median"] - royer_h01w_spl
    spread = float(np.std(offs, ddof=1))
    hyp = "A" if abs(offset) <= 6 else "B"
    sens = pd.read_sql("SELECT * FROM dg_royer_2016_royer_sensitivity", con)
    def upa_per_count(site):
        r = sens[sens.site == site].iloc[0]; return 20 * np.log10(r.uV_per_count * 1e-6) - r["sensitivity_dB_re_1uPa_per_V"]
    sB = float(upa_per_count("H01") - upa_per_count("SSEIR"))
    b.check("F09", "C3(iii) pre-registered decision: Royer colour scale calibrated at every station (A: |H01W2 offset| <= 6 dB) or counts (B)",
            "PASS", f"offset {offset:+.2f} dB (C1 {h1['median']:.2f} minus Royer H01W2 {royer_h01w_spl:.2f}); per-panel offsets "
            + "/".join(f"{o:+.2f}" for o in offs) + f"; hypothesis {hyp}; under B an OHASISBIO station would need {-sB:+.2f} dB more (Table 3: H01 "
            f"{upa_per_count('H01'):.1f}, OHASISBIO {upa_per_count('SSEIR'):.1f} dB re 1 uPa per count)")
    shift = offset if hyp == "A" else offset - sB
    sig3 = float(np.sqrt(h1["sigma"] ** 2 + 1.5 ** 2 + spread ** 2))
    oh_rows = []
    for stn, site in [("sseir", "SSEIR"), ("swams3", "SWAMS3")]:
        for (t0, t1, lab) in [(PANELS["a"][1], PANELS["c"][2], "00:27-00:57 (Kadri span)"), ("2014-03-08T00:00:00Z", "2014-03-08T02:00:00Z", "00:00-02:00 (Royer appendix)")]:
            v, tabs = royer(stn, t0, t1)
            floor = float(np.mean(v <= 70.0 + 1e-9))
            for stat, val in [("median", np.median(v)), ("p10", np.percentile(v, 10)), ("p90", np.percentile(v, 90))]:
                oh_rows.append(dict(site_id=site, sensor_or_element="Royer 2016 appendix spectrogram", context="MH370 8 Mar 2014", period_start_utc=t0, period_end_utc=t1,
                                    period_note=lab + f"; {len(v)} pixel columns; {floor:.1%} at the 70 dB colour floor", band_lo_hz=5.0, band_hi_hz=40.0, band_label="5-40 Hz",
                                    quantity_id="rms_level", statistic=stat, value=round(float(val + BW_5_40 + shift), 3), unit="dB re 1 uPa",
                                    original_value=round(float(val), 3), original_unit="dB (Royer colour scale, mean of dB over 5-40 Hz rows)", original_field="psd_db_5_40",
                                    averaging="spectrogram pixel column (about 1.6 s); statistic over columns; + 10 log10(35 Hz) + transfer offset",
                                    n_items=int(len(v)), method="transfer calibration via H01W2 (Royer 2016 spectrograms)", source_id="royer2016", dataset_id=f"royer2016_spectrograms_{stn}",
                                    segment_file=None, input_file="DB:" + ";".join(tabs), input_sha256="see imported_table", registry_entry_id=REG, registry_status=RSTATUS,
                                    role="background (event day, transfer calibration)", caveat=ROYER_CAVEAT + f" Offset {shift:+.2f} dB from H01W2 against the C1 trace level (hypothesis {hyp}).",
                                    import_block="fix_C3", uncertainty_db=round(sig3, 3) if stat == "median" else None,
                                    uncertainty_note=(f"1 sigma {sig3:.2f} dB = C1 {h1['sigma']:.2f} + colour digitisation 1.50 + spread of the three 10-min H01W2 offsets "
                                                      f"{spread:.2f}, in quadrature") if stat == "median" else None))
            b.ins("noise_fix_result", dict(item="C3(iii)", site_id=site, quantity=f"5-40 Hz SPL by transfer, median, {lab}", value=round(float(np.median(v) + BW_5_40 + shift), 3),
                                           unit="dB re 1 uPa", sigma=round(sig3, 3), detail=f"Royer median {np.median(v):.2f} + {BW_5_40:.2f} + offset {shift:+.2f}"))
    b.ins("noise_estimate", oh_rows)
    b.ins("noise_fix_result", dict(item="C3(iii)", site_id="H01W", quantity="transfer offset (C1 trace minus Royer H01W2 colour SPL, 00:27-00:57)", value=round(offset, 3), unit="dB",
                                   sigma=round(spread, 3), detail=f"per-panel offsets {', '.join(f'{o:+.2f}' for o in offs)}; hypothesis {hyp}"))

    # ------------------------------------------------------------------ C3 (ii) one table of H01W / H08S 5-40 Hz levels
    cmp = []
    for st in ["H01W", "H08S"]:
        r = q("SELECT march_p50, blackman2003_median FROM ims_noise_vs_reference WHERE station=? AND element='all' AND subset='clock_window' AND quantity LIKE 'band SPL 5-40 Hz%'", (st,))
        if not r:
            r = q("SELECT avg(march_p50), avg(blackman2003_median) FROM ims_noise_vs_reference WHERE station=? AND subset='clock_window' AND quantity LIKE 'band SPL 5-40 Hz%'", (st,))
        cmp.append(dict(site_id=st, source="Blackman et al. 2004 (traced)", year_or_period="May-June 2003", statistic="median over QC-passed panels", spl_5_40_db=round(r[0][1], 2),
                        sigma_db=None, derivation="ims_noise_vs_reference.blackman2003_median (producer: recomputed from the QC-passed Blackman panels)", noise_ids=None,
                        method="traced from published figure, converted with station calibration"))
        ne = q("""SELECT noise_id, value, n_items FROM noise_estimate WHERE import_block='imp_ims_march_noise_percentiles' AND site_id=? AND band_label='5-40 Hz'
                  AND sensor_or_element='all' AND statistic='median' AND period_note LIKE 'blocks / clock_window%'""", (st,))
        cmp.append(dict(site_id=st, source="open raw IMS (EarthScope)", year_or_period="March 2015-2019, arrival-window clock hours", statistic="median over element-minutes",
                        spl_5_40_db=round(ne[0][1], 2) if ne else None, sigma_db=None, derivation="noise_estimate (stage 3 import of ims-march-noise-percentiles.csv)",
                        noise_ids=",".join(str(x[0]) for x in ne), method="measured from raw recording (EarthScope, response removed)"))
        key = ("H01W", "Fig. 9 panels a-c", "quiet") if st == "H01W" else ("H08S", "Fig. 9 panel d", "quiet")
        cmp.append(dict(site_id=st, source="Kadri 2024 Fig. 9 trace (fix C1)", year_or_period="8 Mar 2014, " + ("00:27-00:57" if st == "H01W" else "01:00-01:10, between shots"),
                        statistic="median 1-s RMS", spl_5_40_db=round(c1_res[key]["median"], 2), sigma_db=round(c1_res[key]["sigma"], 2), derivation="fix C1",
                        noise_ids=str(ids.get(f"{key[0]}|{key[1]}|" + ("background (event day, trace)" if st == "H01W" else "background between airgun shots (event day, trace)"))),
                        method="digitised from published pressure trace"))
        col = pd.read_sql("""SELECT noise_id, sensor_or_element, band_lo_hz, band_hi_hz, value FROM noise_estimate WHERE source_id='kadri2024' AND site_id=? AND statistic='median'
                             AND method LIKE 'digitised from published spectrogram%'""", con, params=(st,))
        for panel, g in col.groupby("sensor_or_element"):
            spl = float(10 * np.log10(np.sum(10 ** (g.value / 10) * (g.band_hi_hz - g.band_lo_hz))))
            cmp.append(dict(site_id=st, source="Kadri 2024 Fig. 9 spectrogram colour", year_or_period="8 Mar 2014, " + panel, statistic="median colour over the panel, per 1/3 octave",
                            spl_5_40_db=round(spl, 2), sigma_db=None, derivation=f"10 log10(sum of 1/3-octave PSD x bandwidth), bands {g.band_lo_hz.min():.2f}-{g.band_hi_hz.max():.2f} Hz",
                            noise_ids=",".join(map(str, g.noise_id)), method="digitised from published spectrogram colour"))
    cmp.append(dict(site_id="H01W", source="Royer 2016 H01W2 spectrogram colour (raw reading)", year_or_period="8 Mar 2014, 00:27-00:57", statistic="median over pixel columns",
                    spl_5_40_db=round(royer_h01w_spl, 2), sigma_db=None, derivation="median psd_db_5_40 (mean of dB over 5-40 Hz rows) + 10 log10(35 Hz); no colour-statistic correction",
                    noise_ids=None, method="digitised from published spectrogram colour"))
    v02, _ = royer("h01w2", "2014-03-08T00:00:00Z", "2014-03-08T02:00:00Z")
    cmp.append(dict(site_id="H01W", source="Royer 2016 H01W2 spectrogram colour (raw reading)", year_or_period="8 Mar 2014, 00:00-02:00", statistic="median over pixel columns",
                    spl_5_40_db=round(float(np.median(v02) + BW_5_40), 2), sigma_db=None, derivation="as above", noise_ids=None, method="digitised from published spectrogram colour"))
    b.ins("noise_compare_5_40", cmp)
    con.executescript("""
    CREATE VIEW v_ims_noise_5_40_compare AS SELECT site_id, source, year_or_period, statistic, spl_5_40_db, sigma_db, method, derivation, noise_ids FROM noise_compare_5_40 ORDER BY site_id, spl_5_40_db;
    CREATE VIEW v_noise_summary AS
    SELECT n.noise_id, n.site_id, s.name AS site_name, n.context, n.band_label, n.band_lo_hz, n.band_hi_hz, q.name AS quantity, n.statistic,
           round(n.value, 2) AS value, n.unit, n.uncertainty_db, n.averaging, n.n_items, n.method, n.role, n.registry_entry_id, n.registry_status, n.caveat,
           p.preferred_8mar2014, p.preference_reason, n.import_block
    FROM noise_estimate n LEFT JOIN site s USING(site_id) JOIN quantity_def q USING(quantity_id) LEFT JOIN noise_preference p USING(noise_id)
    WHERE n.statistic != 'value';
    CREATE VIEW v_noise_8mar2014 AS SELECT * FROM v_noise_summary WHERE context = 'MH370 8 Mar 2014';
    """)
    nn = q("SELECT count(*) FROM v_noise_8mar2014 WHERE site_id IN ('H01W','H08S') AND preferred_8mar2014 IS NULL")[0][0]
    np1 = q("SELECT site_id, count(*) FROM v_noise_8mar2014 WHERE preferred_8mar2014 = 1 AND statistic = 'median' GROUP BY site_id")
    b.check("F10", "Every 8 Mar 2014 H01W/H08S row in v_noise_8mar2014 carries a preference mark; one preferred median row per station (plus its p10/p90 rows)",
            nn == 0 and dict(np1) == {"H01W": 1, "H08S": 1}, f"unmarked {nn}; preferred median rows {np1}")
    old = q("SELECT count(*) FROM noise_estimate WHERE source_id='kadri2024' AND method LIKE 'digitised from published spectrogram%'")[0][0]
    b.check("F11", "The Kadri spectrogram-colour rows are kept (not deleted; caveat unchanged)", old > 0 and q("SELECT count(*) FROM noise_estimate WHERE caveat LIKE 'biased low: 64 dB colour floor%'")[0][0] > 0, f"{old} rows kept")
    con.execute("DELETE FROM meta WHERE key LIKE 'stage4_%'")
    for k, v in dict(stage4_schema=STAGE, stage4_built_utc=BUILD_UTC, stage4_scope="Noise caveat fixes C1-C3 (26 Oct 2026); adds rows only; views v_noise_summary / v_noise_8mar2014 carry preferred_8mar2014.").items():
        b.ins("meta", dict(key=k, value=v))
    con.commit(); con.close()
    for c in b.checks:
        print(f"{c[0]} {c[2]:6s} {c[1][:120]} | {c[3][:400]}")
    if any(c[2] == "FAIL" for c in b.checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
