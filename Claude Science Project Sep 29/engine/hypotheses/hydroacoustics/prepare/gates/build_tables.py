"""Potential-signal tables 1-3 from the detection register v2 (overnight 23-24 Oct 2026, Pete's request 03:20 UTC 23 Oct).

Table 1  MULTI-SITE (pairs and triples) whose lag gives a locus on the 7th arc, POSSIBLE in terms of power, and NOT time-consistent
         with a Royer 2016 known event at any member receiver.
Table 2  SINGLE-SITE rows with an implied source position, same tests.
Table 3  rows (any set size) that pass the physical tests but correlate in time with a known event: a Royer 2016 event
         (data-based tolerance, X05) or an H08S airgun shot (data-based window, X04). Each row names the event.
Physical tests (a row failing any one is in no table; counts in tables_summary.json):
  whole band below the recorder corner; no-information receiver (Scott Reef 3250); path crosses land; implied impact before
  00:19:29; coupling > 1 at the q99 run J energy (IMPOSSIBLE); coupling or locus not assessable.
"Possible in terms of power" = coupling needed at the q99 run J impact energy at the locus <= 1 (physical limit). Each row also
gives p_prior_eta_ge_needed = P(eta >= that coupling) under the log-uniform prior on [1e-6, 1] (X03), and the multiple of the
F-35A value 2.26e-3 (X02). These are labels for the reader, not a detection claim. An airgun-shot coincidence is a label, not
an exclusion (Pete, 23 Oct): such rows stay in tables 1/2 with the label and are also listed in table 3.
Usage: python build_tables.py <register_v2_dir> <out_dir>
"""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd

HARD = {"no-information receiver": "no-information receiver (3250)", "band below corner": "whole band below corner",
        "path crosses land": "path crosses land", "implied impact before 00:19:29": "implied impact before 00:19:29",
        "impossible coupling": "coupling > 1 at q99 energy", "not assessed": "not assessable (no locus/position or coupling)"}


def hard_reasons(flags):
    f = str(flags); out = []
    for k, v in HARD.items():
        if k == "band below corner":
            if re.search(r"(^|; )band below corner", f): out.append(v)
        elif k in f: out.append(v)
    if re.search(r"(^|; )impossible \(coupling", f): out.append(HARD["impossible coupling"])
    return out


def royer_events(s):
    return re.findall(r"Royer event ([^;]+?) predicted ([\d:.]+) \+/- ([\d.]+) s", str(s))


def main(reg, out):
    reg, out = Path(reg), Path(out); out.mkdir(parents=True, exist_ok=True)
    summ = json.load(open(reg / "summary.json")); cover = summ["royer_window_coverage_by_receiver"]
    T = {}
    for kind in ("singles", "pairs", "triples"):
        df = pd.read_csv(reg / f"register_{kind}.csv", low_memory=False, dtype={"rx": str})
        df.insert(0, "set_type", kind[:-1]); df.insert(0, "reg_row", np.arange(len(df)))
        df["hard"] = df["flags"].map(hard_reasons)
        df["royer_match"] = df["flags"].fillna("").str.contains("time-consistent with Royer")
        df["shot_coincident"] = df["flags"].fillna("").str.contains("airgun-shot coincidence")
        ucols = ["known_event_uncorrected_figure"] if kind == "singles" else [c for c in df.columns if c.endswith("_known_event_uncorrected_figure")]
        df["royer_timebase_dependent"] = df[ucols].apply(lambda r: "; ".join(str(v) for v in r if isinstance(v, str) and v not in ("n/a", "NO_KNOWN_EVENT_MATCH")), axis=1) if ucols else ""
        df["royer_timebase_dependent"] = np.where(df.royer_match, "", df["royer_timebase_dependent"])
        T[kind] = df
    ok = {k: d[d.hard.map(len) == 0] for k, d in T.items()}
    keep_m = ["set_type", "reg_row", "rank_lnLR", "lnLR", "members", "lag_s", "locus_lat", "locus_lon", "n_arc_loci", "locus_D0_mass_within_1deg",
              "implied_impact_utc", "E_q99_at_locus_J", "eta_at_q99E", "x_metz_2.26e-3", "p_prior_eta_ge_needed", "coupling_check", "royer_timebase_dependent", "flags"]
    t1 = pd.concat([ok["pairs"], ok["triples"]]); t1 = t1[~t1.royer_match]
    t1 = t1.sort_values("lnLR", ascending=False)
    shotcols = [c for c in t1.columns if re.match(r"m\d_(shot_check|shot_dt_s|shot_p_related|shot_residual|band_check|known_event_uncorrected_figure)$", c)]
    t1 = t1[[c for c in keep_m if c in t1.columns] + shotcols]
    t1.insert(0, "table1_id", [f"M{i+1:03d}" for i in range(len(t1))])
    keep_s = ["set_type", "reg_row", "rank_lnLR", "lnLR", "rx", "time_utc", "det", "band", "p", "source", "kadri_label", "implied_source", "implied_impact_utc",
              "E_q99_at_src_J", "eta_at_q99E", "x_metz_2.26e-3", "p_prior_eta_ge_needed", "coupling_check", "band_check", "shot_check", "shot_dt_s",
              "shot_p_related", "shot_residual", "royer_timebase_dependent", "flags"]
    t2 = ok["singles"][~ok["singles"].royer_match].sort_values("lnLR", ascending=False)
    t2 = t2[[c for c in keep_s if c in t2.columns]]; t2.insert(0, "table2_id", [f"S{i+1:03d}" for i in range(len(t2))])
    rows = []
    for kind, d in ok.items():
        for _, r in d[d.royer_match | d.shot_coincident | (d.royer_timebase_dependent.astype(str) != "")].iterrows():
            if kind == "singles":
                mem = [(r.rx, r.time_utc, r.known_event, r.get("shot_check"), r.get("shot_dt_s"), r.get("shot_p_related"))]
            else:
                n = 2 if kind == "pairs" else 3; names = re.findall(r"(\w+) (\d\d:\d\d:\d\d)", r.members)
                mem = [(names[i][0], names[i][1], r.get(f"m{i+1}_known_event"), r.get(f"m{i+1}_shot_check"), r.get(f"m{i+1}_shot_dt_s"), r.get(f"m{i+1}_shot_p_related")) for i in range(min(n, len(names)))]
            ev = []
            for rx, t, ke, sc, sdt, sp in mem:
                for e, pt, tol in royer_events(ke):
                    ev.append(f"{rx} {t}: Royer 2016 event {e}, predicted {pt} +/- {tol} s (chance match at {rx} about {100*cover.get(str(rx), {}).get('fraction_of_0000_0200', np.nan):.0f} %)")
                if isinstance(ke, str) and "pick bar" in ke or (isinstance(ke, str) and "arrow" in ke):
                    ev.append(f"{rx} {t}: {ke}")
                if sc == "COINCIDENT_WITH_SHOT" or False:
                    ev.append(f"{rx} {t}: airgun shot, dt {sdt:+.2f} s, P(shot-related) {sp:.2f}")
            if str(r.royer_timebase_dependent):
                ev.append("TIME-BASE DEPENDENT (H01W): matches only on the uncorrected Royer Fig. 4 time base, not on Table 5 / bias-corrected marks: " + str(r.royer_timebase_dependent))
            rows.append(dict(set_type=kind[:-1], reg_row=r.reg_row, royer_timebase_dependent=bool(str(r.royer_timebase_dependent)), rank_lnLR=r.rank_lnLR, lnLR=r.lnLR, members=r.members if kind != "singles" else f"{r.rx} {r.time_utc} [{r.band}] {r.det}",
                             locus_or_source=(f"{r.locus_lat:.2f}, {r.locus_lon:.2f}" if kind != "singles" else r.implied_source), implied_impact_utc=r.implied_impact_utc,
                             royer_match=bool(r.royer_match), shot_coincident=bool(r.shot_coincident), in_table_1_or_2=not bool(r.royer_match), known_events="; ".join(ev)))
    t3 = pd.DataFrame(rows).sort_values(["royer_match", "lnLR"], ascending=[False, False]); t3.insert(0, "table3_id", [f"K{i+1:03d}" for i in range(len(t3))])
    t1.to_csv(out / "table1_multisite.csv", index=False); t2.to_csv(out / "table2_single_site.csv", index=False); t3.to_csv(out / "table3_known_event_correlates.csv", index=False)
    hs = {k: pd.Series([x for h in d.hard for x in h]).value_counts().to_dict() for k, d in T.items()}
    s = dict(register=str(reg), n_register={k: len(d) for k, d in T.items()}, n_pass_physical={k: len(d) for k, d in ok.items()},
             table1=dict(n=len(t1), pairs=int((t1.set_type == "pair").sum()), triples=int((t1.set_type == "triple").sum()), with_shot_label=int(t1["flags"].str.contains("airgun").sum())),
             table2=dict(n=len(t2), by_rx=t2.rx.value_counts().to_dict(), with_shot_label=int(t2["flags"].str.contains("airgun").sum())),
             table3=dict(n=len(t3), royer=int(t3.royer_match.sum()), shot=int(t3.shot_coincident.sum()), timebase_dependent_only=int((t3.royer_timebase_dependent & ~t3.royer_match).sum())),
             table1_timebase_dependent=int((t1.royer_timebase_dependent.astype(str).fillna("") != "").sum()) if "royer_timebase_dependent" in t1 else None,
             table2_timebase_dependent=int((t2.royer_timebase_dependent.fillna("").astype(str) != "").sum()),
             singles_without_position_by_rx=T["singles"][T["singles"].hard.map(lambda h: any("not assessable" in x for x in h))].rx.value_counts().to_dict(), hard_exclusions_by_reason=hs,
             royer_chance_fraction=cover)
    json.dump(s, open(out / "tables_summary.json", "w"), indent=1, default=str); print(json.dumps({k: s[k] for k in ("n_pass_physical", "table1", "table2", "table3")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
