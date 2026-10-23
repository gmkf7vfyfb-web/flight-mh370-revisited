"""Step 3: whale-call catalogue, validation tables and candidate cross-check (whale-call track, 23 Oct 2026).

Inputs : whale/work/det/*.parquet (process_imos.py), SEANOE 46124 + 51007 (whale/downloads/), Royer 2016 digitised
         spectrogram grids (digitise_royer_2016.py output dir), candidate lists (repo + mh370-exchange v3 tables).
Outputs: <out>/whale_call_catalogue_8mar2014.csv, whale_call_catalogue_backgrounds.csv.gz,
         candidate_crosscheck.csv, validation_*.csv, royer_26hz_lines.csv, seanoe_zcalls_8mar2014.csv
Usage  : python build_catalogue.py <det_dir> <royer_spec_dir> <downloads_dir> <repo_handover_dir> <potential_signals_v3_dir> <kadri_dir> <out_dir>
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_io as io  # noqa: E402

DET, RSPEC, DL, HH, PS, KD, OUT = [Path(a) for a in sys.argv[1:8]]
OUT.mkdir(parents=True, exist_ok=True)
DAY0 = pd.Timestamp("2014-03-08", tz="UTC")
BB_THR = 9.0          # broadband index (dB above 25th-pct floor, 85-120 Hz) above which a detection is a broadband event
SPEC = {"PB_SEIO_I": "PB", "PB_SEIO_II": "PB", "PB_SEIO_III": "PB", "OMURA_TONE": "OMURA", "ABW_Z": "ABW",
        "CHAGOS": "CHAGOS", "PB_SWIO_U1": "PB_SWIO", "OMURA_PULSED": "OMURA"}
SPECIES_NAME = {"PB": "pygmy blue whale, south-east Indian Ocean ('Australian') song",
                "OMURA": "Omura's whale (Australian song)", "ABW": "Antarctic blue whale Z-call",
                "CHAGOS": "'Chagos' (Diego Garcia downsweep) blue whale song",
                "PB_SWIO": "pygmy blue whale, Madagascan song (unit 1)"}
TYPE_DESC = {"PB_SEIO_I": "song unit I: ~19 Hz tone stepping to ~21 Hz, harmonics", "PB_SEIO_II": "song unit II: upsweep ~20.5->23.5 Hz, 3rd harmonic ~62-70 Hz",
             "PB_SEIO_III": "song unit III: flat 17.3-19.8 Hz tone >= 20 s, harmonics", "ABW_Z": "Z-call: 26.1 Hz tone, downsweep, 18.5-19 Hz tone",
             "OMURA_TONE": "tonal end of song: 25 Hz then 19.8 Hz (z-shape)", "OMURA_PULSED": "noisy pulsed song unit 20-45 Hz, 2.5-9 s",
             "CHAGOS": "unit 1 down-tone ~31->28 Hz then 23 Hz tone", "PB_SWIO_U1": "unit 1 tone 33.5-34.3 Hz, 12 s"}
# Manual-review caps (spectrogram review of random detections, see METHODS.md section 5)
CAPS = [("Scott Reef", "PB_SEIO_I", "manual review: hits sit inside Omura's whale song; pygmy blue unit I not confirmed at Scott Reef"),
        ("Scott Reef", "PB_SEIO_III", "not confirmed at Scott Reef (inside Omura chorus)"),
        ("Perth Canyon", "OMURA_TONE", "manual review: hits sit on pygmy blue song tones; Omura's whale not confirmed at Perth Canyon"),
        ("Portland", "OMURA_TONE", "Omura's whale not confirmed at Portland"),
        ("Perth Canyon", "PB_SWIO_U1", "Madagascan type not confirmed at Perth Canyon"),
        ("Scott Reef", "ABW_Z", "manual review: hits sit inside Omura chorus; Z-call not confirmed"),
        ("Portland", "ABW_Z", "manual review: no visible Z-call; possible only"),
        ("Perth Canyon", "ABW_Z", "possible only")]


def load_det():
    rd = lambda pat: pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(str(DET / pat)))], ignore_index=True)  # noqa: E731
    TT, PP, RR = rd("templates_*.parquet"), rd("pulses_*.parquet"), rd("records_*.parquet")
    for X in (TT, PP, RR):
        X["site"] = X.cid.astype(str).map(io.SITE)
    return TT, PP, RR


def add_q(T, hours):
    """Target-decoy: q = monotone min of n_null(>=s)/n_real(>=s) per family x site."""
    T = T.copy()
    T["q"] = np.nan
    T["fa_per_h"] = np.nan
    for (fam, site), g in T.groupby(["family", "site"]):
        r = g[g.kind == "real"].score.values
        n = np.sort(g[g.kind == "null"].score.values)
        idx = g.index[g.kind == "real"]
        o = np.argsort(-r)
        rs = r[o]
        n_real = np.arange(1, len(rs) + 1)
        n_null = len(n) - np.searchsorted(n, rs, side="left")
        fdr = np.minimum(1, n_null / n_real)
        T.loc[idx[o], "q"] = np.minimum.accumulate(fdr[::-1])[::-1]
        T.loc[idx[o], "fa_per_h"] = n_null / hours[site]
    return T


def suppress(R, qmax=0.5, min_overlap=0.4):
    R = R[R.q <= qmax].copy()
    R["masked_by"] = ""
    out = []
    for _, g in R.groupby("src"):
        g = g.sort_values("strength", ascending=False)
        acc = []
        for i, r in g.iterrows():
            a0, a1 = r.t_start, r.t_start + r.dur
            m = ""
            for (b0, b1, fam) in acc:
                if max(0, min(a1, b1) - max(a0, b0)) / r.dur >= min_overlap and fam != r.family:
                    m = fam
                    break
            if m:
                g.at[i, "masked_by"] = m
            else:
                acc.append((a0, a1, r.family))
        out.append(g)
    return pd.concat(out)


def structure_tags(R, PP):
    R = R.copy()
    R["structure"] = ""
    om = PP[PP.family == "OMURA_PULSED"]
    omg = {s: g.t_peak.values for s, g in om.groupby("src")}
    for src, g in R.groupby("src"):
        pb = g[g.family.str.startswith("PB_SEIO")]
        for i, r in g.iterrows():
            tags = []
            if r.family.startswith("PB_SEIO"):
                for j, o in pb.iterrows():
                    if j == i:
                        continue
                    d = o.t_start - r.t_start
                    pair = (r.family, o.family)
                    if (pair == ("PB_SEIO_II", "PB_SEIO_III") and 38 <= d <= 62) or (pair == ("PB_SEIO_III", "PB_SEIO_II") and -62 <= d <= -38):
                        tags.append("II->III")
                    if (pair == ("PB_SEIO_I", "PB_SEIO_II") and 38 <= d <= 60) or (pair == ("PB_SEIO_II", "PB_SEIO_I") and -60 <= d <= -38):
                        tags.append("I->II")
                    if o.family == r.family:
                        for nm, (a, b) in [("P3", (165, 210)), ("P2", (80, 100)), ("P1", (43, 52))]:
                            if a <= abs(d) <= b:
                                tags.append(f"ISI_{nm}")
            elif r.family == "OMURA_TONE":
                tp = omg.get(src, np.array([]))
                if np.any((tp >= r.t_start - 12) & (tp <= r.t_start + 1)):
                    tags.append("pulsed_units_before_tone")
            elif r.family in ("ABW_Z", "CHAGOS"):
                oth = g[(g.family == r.family) & (g.index != i)].t_start.values
                lo, hi = (40, 80) if r.family == "ABW_Z" else (180, 210)
                if np.any((np.abs(oth - r.t_start) >= lo) & (np.abs(oth - r.t_start) <= hi)):
                    tags.append("ISI_Z" if r.family == "ABW_Z" else "ISI_Chagos")
            R.at[i, "structure"] = ";".join(sorted(set(tags)))
    return R


def context(C):
    C = C.copy()
    C["note"] = ""
    for _, g in C.groupby("src"):
        cnt = g[g.confidence == "high"].species.value_counts()
        if cnt.empty or cnt.iloc[0] < 2:
            continue
        ctx = cnt.index[0]
        off = g[(g.species != ctx) & (g.confidence != "high")]
        C.loc[off.index, "confidence"] = "low"
        C.loc[off.index, "note"] = f"off-context: record has >=2 high-confidence {ctx} calls; may be the same callers (cross-talk)"
    return C


def build():
    TT, PP, RR = load_det()
    RR["lvl_dev"] = RR.lvl_5_40 - RR.groupby("cid").lvl_5_40.transform("median")
    qc_bad = set(RR[((RR.lvl_dev < -15) & (RR.cid.astype(str) != "3250")) | (RR.lvl_5_40 < 60)].src)
    hours = RR[~RR.src.isin(qc_bad)].groupby("site").dur.sum() / 3600
    T = TT[~TT.src.isin(qc_bad)].copy()
    T["broadband"] = T.bb_db > BB_THR
    Tq = add_q(T[~T.broadband], hours)
    nul99 = Tq[Tq.kind == "null"].groupby(["family", "site"]).score.quantile(.99)
    R = Tq[Tq.kind == "real"].copy()
    R["strength"] = R.score - [nul99[(a, b)] for a, b in zip(R.family, R.site)]
    R = suppress(R)
    R = R[R.masked_by == ""].copy()
    R = structure_tags(R, PP)
    hs = R.structure != ""
    R["confidence"] = np.select([(R.q <= 0.05) & hs, (R.q <= 0.05) | ((R.q <= 0.2) & hs), R.q <= 0.5], ["high", "medium", "low"], "none")
    R["species"] = R.family.map(SPEC)
    R = context(R)
    m = R.family == "CHAGOS"
    R.loc[m, "confidence"] = "low"
    R.loc[m, "note"] = (R.loc[m, "note"] + " | Chagos type not confirmed in manual review (hits sit inside Omura or pygmy blue song); possible only").str.strip(" |")
    for s, fm, nt in CAPS:
        m = (R.site == s) & (R.family == fm)
        R.loc[m, "confidence"] = "low"
        R.loc[m, "note"] = (R.loc[m, "note"] + " | " + nt).str.strip(" |")
    R["t_start_utc"] = pd.to_datetime(R.t0_utc) + pd.to_timedelta(R.t_start, unit="s")
    R["t_end_utc"] = R.t_start_utc + pd.to_timedelta(R.dur, unit="s")
    # Omura noisy pulsed units
    op = PP[(PP.family == "OMURA_PULSED") & (~PP.src.isin(qc_bad))].copy()
    op["t_start"] = op.t_peak - op.dur / 2
    op["t_start_utc"] = pd.to_datetime(op.t0_utc) + pd.to_timedelta(op.t_start, unit="s")
    op["t_end_utc"] = op.t_start_utc + pd.to_timedelta(op.dur, unit="s")
    tone_by = {s: g for s, g in R[R.family == "OMURA_TONE"].groupby("src")}
    conf, note = [], []
    for r in op.itertuples():
        g = tone_by.get(r.src)
        hi_ctx = g is not None and (g.confidence == "high").sum() >= 2
        follows = g is not None and np.any((g.t_start - r.t_peak >= 0) & (g.t_start - r.t_peak <= 14) & g.confidence.isin(["high", "medium"]))
        if r.site == "Scott Reef" and follows:
            conf.append("high"); note.append("noisy pulsed unit followed within 14 s by an Omura tonal end (song structure)")
        elif r.site == "Scott Reef" and hi_ctx:
            conf.append("medium"); note.append("noisy pulsed 20-45 Hz unit inside a record with >=2 high-confidence Omura songs")
        else:
            conf.append("low"); note.append("20-45 Hz noisy pulsed band event; species not confirmed")
    op = op.assign(family="OMURA_PULSED", species="OMURA", confidence=conf, note=note, f_lo=20.0, f_hi=45.0,
                   band15_30_excess_db=op.excess_db, structure=np.where(np.array(conf) == "high", "pulsed->tone", ""))
    cols = ["cid", "site", "set", "src", "t0_utc", "family", "species", "t_start", "dur", "t_start_utc", "t_end_utc", "f_lo", "f_hi",
            "score", "q", "fa_per_h", "band15_30_excess_db", "band15_30_level_db", "bb_db", "structure", "confidence", "note"]
    CAT = pd.concat([R.reindex(columns=cols), op.reindex(columns=cols)], ignore_index=True)
    CAT["type_description"] = CAT.family.map(TYPE_DESC)
    CAT["species_name"] = CAT.species.map(SPECIES_NAME)
    CAT["source"] = "IMOS raw record " + CAT.src.str.split("/imos/").str[-1]
    return CAT, TT, PP, RR, Tq, qc_bad, hours


if __name__ == "__main__":
    CAT, TT, PP, RR, Tq, qc_bad, hours = build()
    out_cols = ["site", "cid", "t_start_utc", "t_end_utc", "species", "species_name", "family", "type_description", "f_lo", "f_hi",
                "confidence", "q", "fa_per_h", "score", "band15_30_excess_db", "band15_30_level_db", "structure", "note", "source", "set"]
    ev = CAT[CAT.set == "event"].sort_values(["cid", "t_start_utc"])
    ev[out_cols].to_csv(OUT / "whale_call_catalogue_imos_8mar2014.csv", index=False, float_format="%.3f")
    CAT[CAT.set == "background"].sort_values(["cid", "t_start_utc"])[out_cols].to_csv(OUT / "whale_call_catalogue_imos_backgrounds.csv.gz", index=False, float_format="%.3f")
    # validation: target-decoy counts
    v = Tq.groupby(["site", "family", "kind"]).score.agg(["size", lambda s: (s >= 8).sum()]).rename(columns={"size": "n_peaks", "<lambda_0>": "n_score_ge_8"}).unstack("kind")
    v.columns = [f"{a}_{b}" for a, b in v.columns]
    v.to_csv(OUT / "validation_target_decoy_counts.csv")
    pd.crosstab([CAT.site, CAT.family], CAT.confidence).to_csv(OUT / "validation_confidence_counts.csv")
    json.dump(dict(n_records=int(len(RR)), records_qc_excluded=sorted(qc_bad), hours_per_site=hours.round(2).to_dict()),
              open(OUT / "run_summary.json", "w"), indent=1)
    print(ev.groupby(["site", "species", "confidence"]).size())
