"""Step 4: cross-check candidate signals against whale-call evidence.
Usage: python crosscheck.py <out_dir (has catalogue)> <det_dir> <royer_spec_dir> <downloads_dir> <repo_handover_dir> <potential_signals_v3_dir> <kadri_data_dir>
Evidence per receiver: IMOS loggers -> this track's catalogue (8 Mar 2014 records); OHASISBIO MAD/NCRO/SSEIR/SWAMS/WKER ->
SEANOE 46124 published Z-call detections (Leroy et al. 2016) + Royer panel spectral test; H01W -> Royer H01W-2 digitised
spectrogram test (17-28 Hz tonal excess vs outside bands); H08S -> not assessable (no frequency-resolved data held).
"""
import glob
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_io as io  # noqa: E402

OUT, DET, RSPEC, DL, HH, PS, KD = [Path(a) for a in sys.argv[1:8]]
IMOS_IDS = {"3250", "3274", "3275", "3315", "3376"}
CONF_RANK = {"high": 3, "medium": 2, "low": 1}
SPECIES_NAME = {"PB": "pygmy blue whale, south-east Indian Ocean ('Australian') song", "OMURA": "Omura's whale (Australian song)",
                "ABW": "Antarctic blue whale Z-call", "CHAGOS": "'Chagos' blue whale song", "PB_SWIO": "Madagascan pygmy blue whale"}
MANUAL = {
    ("3274", "01:04:00"): "no whale call or tonal at candidate time; nothing distinct above 10 Hz",
    ("3274", "01:04:03"): "same as 01:04:00", ("3274", "01:04:04"): "same as 01:04:00",
    ("3274", "01:15:51"): "nothing distinct in 5-80 Hz", ("3274", "01:15:54"): "nothing distinct in 5-80 Hz",
    ("3274", "01:17:37"): "nothing distinct in 5-80 Hz",
    ("3274", "01:33:20"): "nothing distinct at candidate; low-frequency (<15 Hz) energy 30-45 s earlier", ("3274", "01:33:25"): "as 01:33:20",
    ("3275", "01:05:59"): "nothing distinct in 5-80 Hz", ("3275", "01:06:54"): "nothing distinct in 5-80 Hz",
    ("3275", "01:07:46"): "short broadband transient 5-40 Hz, about 4 s, multiple pulses; not whale-like", ("3275", "01:07:47"): "as 01:07:46",
    ("3275", "01:08:24"): "nothing at candidate; the 01:07:46 transient is 40 s earlier", ("3275", "01:08:26"): "as 01:08:24", ("3275", "01:08:33"): "as 01:08:24",
    ("3275", "01:09:23"): "nothing distinct in 5-80 Hz",
    ("3275", "01:20:34"): "two steady tones, 26.9 Hz (about 12 s) and 38.6 Hz (about 5-15 s); biological-like tonal call of unidentified type (no 18-19 Hz downsweep, so not an Antarctic blue Z-call); not an impulsive broadband signal",
    ("3275", "01:20:35"): "as 01:20:34",
    ("3275", "01:22:09"): "faint; nothing distinct", ("3275", "01:22:16"): "faint; nothing distinct",
    ("3275", "01:36:47"): "diffuse 35-70 Hz energy about 8 s; type unidentified (possibly a downswept biological call); not in whale-call catalogue",
    ("3275", "01:37:31"): "nothing distinct in 5-80 Hz",
    ("3315", "00:45:44"): "pygmy blue song present in record (low-confidence unit III tone nearby) but no call energy at the candidate band and time",
    ("3315", "00:49:48"): "pygmy blue unit III (low confidence, +0.8 dB in 15-30 Hz) overlaps; does not account for the candidate energy",
    ("3376", "00:38:03"): "pygmy blue whale unit II upsweep (high confidence) 00:37:40-00:38:08 with 3rd harmonic 65-70 Hz; candidate (20-40 Hz) sits at the end of the unit"}


def tsec(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


def load_royer():
    R = {}
    for p in sorted(glob.glob(str(RSPEC / "*.npz"))):
        z = np.load(p)
        f = z["f_hz"].astype(float)
        o = np.argsort(f)
        R[os.path.basename(p)[:-4]] = dict(t=z["t_utc_s"], f=f[o], P=z["psd_db"].astype(float)[o], station=str(z["station"]).upper().replace("-", ""))
    return R


def royer_test(R, rx, tc, pre=5, post=15, ref=150):
    rx = rx.upper().replace("-", "")
    if rx.startswith("H01W"):
        rx = "H01W2"
    best = None
    for k, v in R.items():
        if v["station"] != rx:
            continue
        t = v["t"]
        if not (t[0] <= tc - pre and tc + post <= t[-1]):
            continue
        res = np.median(np.diff(t))
        if best is None or res < best[1]:
            best = (k, res)
    if best is None:
        return None
    k, res = best
    t, f, P = R[k]["t"], R[k]["f"], R[k]["P"]
    lin = 10 ** (P / 10)
    w = (t >= tc - pre) & (t <= tc + post)
    r_ = ((t >= tc - ref) & (t < tc - pre - 5)) | ((t > tc + post + 5) & (t <= tc + ref))
    if w.sum() < 2 or r_.sum() < 5:
        return None
    ex = 10 * np.log10(lin[:, w].mean(1) / np.median(lin[:, r_], axis=1))
    band = lambda a, b: float(np.mean(ex[(f >= a) & (f <= b)]))  # noqa: E731
    E_wh, E_out = band(17, 28), 0.5 * (band(6, 14) + band(32, 55))
    fm = (f >= 17) & (f <= 28)
    ker = max(1, int(1.5 / np.median(np.diff(f))))
    rm = np.convolve(ex[fm], np.ones(ker) / ker, "same")
    ton = float(rm.max() - np.median(ex[fm]))
    if E_wh >= 2 and E_wh - E_out >= 2 and ton >= 1.5:
        cls = "whale-band tonal excess"
    elif E_out >= 2 or (E_wh >= 2 and E_wh - E_out < 2):
        cls = "broadband excess"
    else:
        cls = "no clear excess"
    return dict(panel=k, res_s=round(res, 2), E_17_28=round(E_wh, 1), E_out=round(E_out, 1), tonal_db=round(ton, 1), f_tonal=round(float(f[fm][np.argmax(rm)]), 1), royer_class=cls)


def candidates():
    c = []
    k1 = pd.read_csv(KD / "kadri-table1-transients.csv")
    for r in k1.itertuples():
        c.append(dict(list="Kadri 2024 Table 1", cand_id=r.event_id, receiver="H01W", time_utc=r.time_utc, band="2-40 (Kadri filter)", cand_note=f"bearing {r.bearing_deg}"))
    ra = pd.read_csv(HH / "data/results-data/digitised/royer-2016/royer_arrivals.csv").dropna(subset=["arrival_utc"])
    for r in ra.itertuples():
        c.append(dict(list="Royer 2016 Table 5 arrivals", cand_id=f'event{r.index}{("/" + r.label) if isinstance(r.label, str) else ""}', receiver=r.station, time_utc=r.arrival_utc, band="0-60 (spectrogram)", cand_note=r.event_class))
    rs = pd.read_csv(HH / "data/results-data/ranked_candidates/ranked_singles.csv")
    for i, r in enumerate(rs.itertuples()):
        c.append(dict(list="module ranked singles (22 Oct)", cand_id=f"row{i + 1}_rankLnLR{r.rank_lnLR}", receiver=str(r.rx), time_utc=r.time_utc, band=r.band, cand_note=f"{r.det}; lnLR {r.lnLR:.2f}; {r.source}"))
    t1 = pd.read_csv(PS / "table1_multisite.csv")
    t2 = pd.read_csv(PS / "table2_single_site.csv")
    for r in t1.itertuples():
        for m in r.members.split(" | "):
            mm = re.match(r"(\S+) (\d\d:\d\d:\d\d) \[(.*)\]", m)
            c.append(dict(list="potential signals v3 table 1", cand_id=r.table1_id, receiver=mm.group(1), time_utc=mm.group(2), band=mm.group(3), cand_note=f"{r.set_type}; lnLR {r.lnLR:.2f}"))
    for r in t2.itertuples():
        c.append(dict(list="potential signals v3 table 2", cand_id=r.table2_id, receiver=str(r.rx), time_utc=r.time_utc, band=r.band, cand_note=f"{r.det}; lnLR {r.lnLR:.2f}"))
    C = pd.DataFrame(c)
    C["t_s"] = C.time_utc.map(tsec)
    return C


def main():
    ev = pd.read_csv(OUT / "whale_call_catalogue_imos_8mar2014.csv", parse_dates=["t_start_utc", "t_end_utc"], dtype={"cid": str})
    day0 = pd.Timestamp("2014-03-08", tz="UTC")
    ev["ts"] = (ev.t_start_utc - day0).dt.total_seconds()
    ev["te"] = (ev.t_end_utc - day0).dt.total_seconds()
    rec = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(str(DET / "records_*.parquet")))], ignore_index=True)
    rec = rec[rec.set == "event"].copy()
    rec["cid"] = rec.cid.astype(str)
    rec["ts"] = (pd.to_datetime(rec.t0_utc) - day0).dt.total_seconds()
    rec["te"] = rec.ts + rec.dur
    Z = pd.read_csv(OUT / "seanoe_zcalls_8mar2014.csv")
    R = load_royer()

    def band_edges(b):
        m = re.findall(r"[\d.]+", str(b))
        return (float(m[0]), float(m[1])) if len(m) >= 2 else (None, None)

    def assess(r):
        rx, tc = str(r.receiver), r.t_s
        lo, hi = band_edges(r.band)
        o = dict(whale_evidence="", whale_call="", call_conf="", call_time="", dt_s=np.nan, call_excess_15_30_db=np.nan, verdict="")
        band_ok = hi is None or hi > 15.5
        if rx in IMOS_IDS:
            cov = rec[(rec.cid == rx) & (rec.ts <= tc) & (rec.te >= tc)]
            if cov.empty:
                o.update(whale_evidence="IMOS: no record covers this time", verdict="not assessable")
                return o
            src = cov.src.iloc[0]
            inrec = ev[ev.source.str.endswith(src.split("/imos/")[-1])]
            o["whale_evidence"] = f"IMOS raw record {os.path.basename(src)}; " + (("whale calls in record: " + ", ".join(f"{k} {v}" for k, v in inrec.groupby("species").size().items())) if len(inrec) else "no whale call detected in record")
            g = ev[(ev.cid == rx) & (ev.ts - 5 <= tc) & (ev.te + 5 >= tc)]
            if g.empty or not band_ok:
                o["verdict"] = "not explained" + ("" if band_ok else " (candidate band below whale-call band)")
                return o
            g = g.assign(cr=g.confidence.map(CONF_RANK)).sort_values(["cr", "q"], ascending=[False, True])
            b = g.iloc[0]
            o.update(whale_call=f"{b.family} ({SPECIES_NAME.get(b.species, b.species)})", call_conf=b.confidence,
                     call_time=f"{b.t_start_utc.strftime('%H:%M:%S')}-{b.t_end_utc.strftime('%H:%M:%S')}", dt_s=round(tc - b.ts, 1),
                     call_excess_15_30_db=round(b.band15_30_excess_db, 1))
            if b.confidence in ("high", "medium") and b.band15_30_excess_db >= 3:
                o["verdict"] = "explained by whale call"
            elif b.confidence in ("high", "medium"):
                o["verdict"] = "possibly explained (whale call present, weak in 15-30 Hz)"
            else:
                o["verdict"] = "possibly explained (low-confidence whale call)"
            return o
        if rx in ("MAD", "NCRO", "SSEIR", "WKER") or rx.startswith("SWAMS"):
            st = "SWAMS" if rx.startswith("SWAMS") else rx
            g = Z[(Z.station == st) & (Z.t_s - 10 <= tc) & (Z.t_s + 25 >= tc)]
            rt = royer_test(R, rx, tc)
            o["whale_evidence"] = f"SEANOE 46124 Z-call detections at {st}" + (f"; Royer panel {rt['panel']}: {rt['royer_class']} (17-28 Hz {rt['E_17_28']} dB, outside {rt['E_out']} dB)" if rt else "")
            if len(g):
                b = g.iloc[np.argmin(abs(g.t_s - tc))]
                o.update(whale_call="Antarctic blue whale Z-call (published detection)", call_conf=f"published, SNR {b.SNR:.1f} dB", call_time=str(b.time_utc), dt_s=round(tc - b.t_s, 1),
                         verdict="coincides with a published Z-call (overlap; Z-call energy 18-26 Hz)")
            else:
                o["verdict"] = "not explained (no published Z-call within -25/+10 s)"
            return o
        if rx.startswith("H01W"):
            rt = royer_test(R, rx, tc)
            if rt is None:
                o.update(whale_evidence="no frequency-resolved H01W data at this time (outside Royer panels)", verdict="not assessable")
                return o
            o["whale_evidence"] = f"Royer H01W-2 {rt['panel']} ({rt['res_s']} s/px): {rt['royer_class']}; 17-28 Hz {rt['E_17_28']} dB, outside {rt['E_out']} dB, tonal {rt['tonal_db']} dB at {rt['f_tonal']} Hz"
            if rt["royer_class"] == "whale-band tonal excess":
                o.update(whale_call="tonal excess in 17-28 Hz (whale-call band; species not resolvable)", verdict="possibly explained (whale-band tonal excess)")
            else:
                o["verdict"] = "not explained (" + rt["royer_class"] + " on Royer H01W-2)"
            return o
        if rx == "H08S":
            o.update(whale_evidence="Kadri Fig. 9 d/e trace only (frequency-blind; airgun shots every 9.98 s dominate)", verdict="not assessable (no frequency-resolved data)")
            return o
        o["verdict"] = "not assessable"
        return o

    C = candidates()
    A = pd.DataFrame([assess(r) for r in C.itertuples()])
    X = pd.concat([C.reset_index(drop=True), A], axis=1)
    X["manual_review"] = [MANUAL.get((r.receiver, r.time_utc), "") for r in X.itertuples()]
    m = X.receiver.eq("3275") & X.time_utc.isin(["01:20:34", "01:20:35"])
    X.loc[m, "verdict"] = "not explained by a catalogued whale call (tonal biological-like signal of unidentified type)"
    m = X.manual_review.str.contains("does not account|no call energy", regex=True)
    X.loc[m, "verdict"] = "not explained (whale song in record, but the call does not account for the candidate energy; manual review)"
    X["verdict_short"] = X.verdict.str.extract(r"^(explained|possibly explained|coincides|not explained|not assessable)")[0]
    X.drop(columns=["t_s"]).to_csv(OUT / "candidate_crosscheck.csv", index=False)
    print(pd.crosstab(X.list, X.verdict_short, margins=True).to_string())


if __name__ == "__main__":
    main()
