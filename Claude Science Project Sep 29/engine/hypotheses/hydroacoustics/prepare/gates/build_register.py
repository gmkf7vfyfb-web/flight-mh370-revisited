"""Build the hydroacoustic detection register (one file per set size) from the 22 Oct ranked tables.

Hydro clean-up run, 23 Oct 2026 (proposal v6, block 2 items 1-4). The register REPLACES, for reading, the ranked
tables (graphics-2026-10-22/ranked, registry status KNOWN_DEFECT) and the withdrawn review feasibility tables.
It keeps every row. It adds check columns from gates.py. It does not rank, select or call any row a candidate.

Inputs (registry ids): ex.ranked (ranked_singles/pairs/triples.csv), in.h08s_shots, ex.weak_signal
(h08s/surviving_candidates.csv), in.gebco_2026, art.royer_crossid, in.royer_2016_digitised (figure marks),
in.geometry_sample (sample.npz, run.json receivers).
Usage: python build_register.py <out dir> --art <handover artifacts dir> [--tol <tolerances dir>] [--ranked <ranked dir>]
Version 2 (overnight 23-24 Oct 2026): --tol uses the data-based X04/X05 tolerances (estimate_tolerances.py); a Royer time match
at ANY receiver is flagged (with the receiver's chance-match fraction in summary.json); --ranked reads re-ranked tables; columns
shot_p_related, known_event_uncorrected_figure (old H01W figure rule, sensitivity) and p_prior_eta_ge_needed (log-uniform
prior on [1e-6, 1]: P(eta >= coupling needed at q99 energy)) are added.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gates as G

HERE = Path(__file__).resolve().parent
MOD = HERE.parent.parent
EX = Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics")
OCEAN = Path("/Users/pete/Downloads/mh370-ocean-data")
RK = EX / "graphics-2026-10-22/ranked"


def why_not(eta, e_used, e_q99):
    """Reason text when coupling_labels returns NOT_COMPUTABLE (verifier finding 23 Oct: one text was used for every cause)."""
    if not (np.isfinite(e_used) and np.isfinite(e_q99)):
        return "not assessed: coupling not computable (energy not available: fewer than 20 run J impacts within 1 deg, or latitude outside the energy grid)"
    if np.isinf(eta):
        return "not assessed: loudness-match coupling infinite in the ranked table (a member receiver has no transmission-loss path, e.g. Scott Reef 3250)"
    return "not assessed: loudness-match coupling not given in the ranked table (NaN)"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--art", required=True); ap.add_argument("--tol"); ap.add_argument("--ranked")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    global RK
    if a.ranked: RK = Path(a.ranked)
    V2 = a.tol is not None
    tj = str(Path(a.tol) / "tolerances.json") if V2 else None; tc = str(Path(a.tol) / "x05_crossid_tolerances.csv") if V2 else None
    rx_pos = json.load(open(EX / "run-j-searches/geometry/run.json"))["receivers"]
    shots = G.Shots(MOD / "results-data/h08s_template/h08s_template_shots.csv", EX / "run-j-weak-signal/h08s/surviving_candidates.csv", tol_json=tj)
    land = G.Land(OCEAN / "gebco/grid/gebco_2026.json")
    royer = G.Royer(Path(a.art) / "a35831fe/239646ad_royer-events-crossid-all-sites.csv",
                    MOD / "results-data/digitised/royer-2016/royer_figure_marks.csv", tol_json=tj, tol_csv=tc)
    en = G.Energy(EX / "run-j-searches/geometry/sample.npz")
    land_cache = {}

    def land_of(lat, lon, rx):
        if rx not in rx_pos:
            return "NO_RECEIVER_POSITION", -1, -1
        k = (round(lat, 3), round(lon, 3), rx)
        if k not in land_cache:
            land_cache[k] = land.path(lat, lon, *rx_pos[rx])
        return land_cache[k]

    def member_cols(rx, t, band, lat, lon):
        tt = G.hms(t)
        sv, sdt, sres = shots.check(rx, tt)
        lv, ln_all, ln_in = land_of(lat, lon, rx) if np.isfinite(lat) else ("NO_POSITION", -1, -1)
        d = dict(_rx=str(rx), band_check=G.band_check(rx, band), receiver_check=G.receiver_check(rx), shot_check=sv,
                 shot_dt_s=sdt, shot_residual=sres, land_check=lv, land_points_inner=ln_in,
                 known_event=royer.check(rx, tt))
        if V2:
            d.update(shot_p_related=shots.p_related(rx, tt), known_event_uncorrected_figure=royer.check_uncorrected(rx, tt))
        return d

    def flags(m):
        f = []
        if m["band_check"].startswith("BELOW"): f.append("band below corner")
        if m["band_check"].startswith("MOSTLY"): f.append("band mostly below corner")
        if m["receiver_check"] != "OK": f.append("no-information receiver")
        if m["shot_check"] == "COINCIDENT_WITH_SHOT": f.append("airgun-shot coincidence")
        if m["land_check"] == "CROSSES_LAND": f.append("path crosses land")
        # Royer windows cover 26-31 % of 00:00-02:00 at IMOS and H08S (chance match ~0.3), 9 % at H01W: flag at H01W only
        if V2:
            if m["known_event"] not in ("NO_KNOWN_EVENT_MATCH", "n/a"): f.append(f"{m.get('_rx')} time-consistent with Royer known event")
        elif m["known_event"] not in ("NO_KNOWN_EVENT_MATCH", "n/a") and m.get("_rx") == "H01W": f.append("H01W time-consistent with Royer known event")
        return f

    summary = {}
    # ---------- singles
    S = pd.read_csv(RK / "ranked_singles.csv", dtype={"rx": str})
    pos = S.implied_source.str.extract(r"([\d.]+)S\s+([\d.]+)E").astype(float)
    S["src_lat"], S["src_lon"] = -pos[0], pos[1]
    rows = []
    for _, r in S.iterrows():
        m = member_cols(r.rx, r.time_utc, r.band, r.src_lat, r.src_lon)
        eq99 = en.at(r.src_lat, "q99")
        eta, xo, xm, clab = G.coupling_labels(r.eta_needed, 1.13e9, eq99)  # eta_needed is at the reference impact E = 1.13 GJ
        tv = G.time_check(G.hms(r.implied_impact_utc))
        f = flags(m) + ([clab.split(" (")[0].lower() + " coupling"] if clab.startswith("IMPOSSIBLE") else []) + (["implied impact before 00:19:29"] if tv.startswith("IMPOSSIBLE") else [])
        if not np.isfinite(r.src_lat): f.append("not assessed: no implied position")
        elif clab == "NOT_COMPUTABLE": f.append(why_not(r.eta_needed, eq99, eq99))
        m.pop("_rx", None)  # flags already computed above
        rows.append({**{k: r[k] for k in ["rank_lnLR", "lnLR", "rx", "time_utc", "det", "band", "p", "source", "kadri_label", "implied_source", "implied_impact_utc", "eta_needed"]},
                     **m, "impact_time_check": tv, "E_q99_at_src_J": eq99, "eta_at_q99E": eta, "x_old_2.1e-4": xo, "x_metz_2.26e-3": xm,
                     "coupling_check": clab, "p_prior_eta_ge_needed": G.p_prior_ge(eta), "flags": "; ".join(f) if f else "none", "n_flags": len(f)})
    RS = pd.DataFrame(rows); RS.to_csv(out / "register_singles.csv", index=False)
    summary["singles"] = dict(n=len(RS), n_no_flags=int((RS.n_flags == 0).sum()),
                              flag_counts=pd.Series([x for s in RS["flags"] for x in s.split("; ") if x != "none"]).value_counts().to_dict())
    print("singles", len(RS), f"{time.time()-t0:.0f}s", flush=True)

    # ---------- pairs and triples
    def sets(df, kind):
        rows = []
        for _, r in df.iterrows():
            if kind == "pairs":
                mem = [(r.rx_a, r.t_a, r.band_a), (r.rx_b, r.t_b, r.band_b)]
            else:
                mem = list(zip(str(r.rxs).split("x"), str(r.times).split(";"), str(r.bands).split(";")))
            lat, lon = r.locus_lat, r.locus_lon
            mcols = [member_cols(str(x), t, b, lat, lon) for x, t, b in mem]
            f = sorted({x for m in mcols for x in flags(m)})
            eq50, eq99 = (en.at(lat, "q50"), en.at(lat, "q99")) if np.isfinite(lat) else (np.nan, np.nan)
            eta, xo, xm, clab = G.coupling_labels(r.eta_level_locus, eq50, eq99)
            tv = G.time_check(G.hms(r.implied_impact_utc))
            if clab.startswith("IMPOSSIBLE"): f.append("impossible coupling")
            if tv.startswith("IMPOSSIBLE"): f.append("implied impact before 00:19:29")
            if not np.isfinite(lat): f.append("not assessed: no arc locus")
            elif clab == "NOT_COMPUTABLE": f.append(why_not(r.eta_level_locus, eq50, eq99))
            base = {k: r[k] for k in ["rank_lnLR", "lnLR", "locus_lat", "locus_lon", "implied_impact_utc", "n_arc_loci", "locus_D0_mass_within_1deg", "eta_level_locus"] if k in r}
            if kind == "pairs":
                base.update(members=f"{r.rx_a} {r.t_a} [{r.band_a}] | {r.rx_b} {r.t_b} [{r.band_b}]", lag_s=r.lag_s, p_perm=r.p_perm)
            else:
                base.update(members=" | ".join(f"{x} {t} [{b}]" for x, t, b in mem))
            for i, m in enumerate(mcols):
                for k, v in m.items():
                    if k != "_rx": base[f"m{i+1}_{k}"] = v
            rows.append({**base, "impact_time_check": tv, "E_q50_at_locus_J": eq50, "E_q99_at_locus_J": eq99, "eta_at_q99E": eta,
                         "x_old_2.1e-4": xo, "x_metz_2.26e-3": xm, "coupling_check": clab, "p_prior_eta_ge_needed": G.p_prior_ge(eta), "flags": "; ".join(f) if f else "none", "n_flags": len(f)})
        return pd.DataFrame(rows)

    for kind, fn in [("pairs", "ranked_pairs.csv"), ("triples", "ranked_triples.csv")]:
        df = pd.read_csv(RK / fn, dtype={"rx_a": str, "rx_b": str, "rxs": str})
        R = sets(df, kind); R.to_csv(out / f"register_{kind}.csv", index=False)
        summary[kind] = dict(n=len(R), n_no_flags=int((R.n_flags == 0).sum()),
                             flag_counts=pd.Series([x for s in R["flags"] for x in s.split("; ") if x != "none"]).value_counts().to_dict())
        print(kind, len(R), f"{time.time()-t0:.0f}s", flush=True)

    rc = royer.c.copy(); cover = {}
    for rx_, grp in rc.groupby(rc.rx.astype(str)):
        iv = sorted((t - w, t + w) for t, w in zip(grp.t, grp.tol_s) if np.isfinite(t))
        tot, cur = 0.0, None
        for lo_, hi_ in iv:
            if cur is None or lo_ > cur[1]: tot += 0 if cur is None else cur[1] - cur[0]; cur = [lo_, hi_]
            else: cur[1] = max(cur[1], hi_)
        tot += 0 if cur is None else cur[1] - cur[0]
        cover[rx_] = dict(window_s=round(tot, 1), fraction_of_0000_0200=round(tot / 7200, 3))
    summary["royer_window_coverage_by_receiver"] = cover
    summary["royer_note"] = "A time match is expected by chance at about the listed fraction for a detection anywhere in 00:00-02:00."
    summary["version"] = "v2 (data-based X04/X05 tolerances; Royer flag at every receiver)" if V2 else "v1"
    if V2: summary["tolerances"] = json.load(open(tj))
    summary["energy_grid"] = dict(lat=en.grid.tolist(), q50=en.q50.tolist(), q99=en.q99.tolist(), n=en.n.tolist())
    summary["built_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(summary, open(out / "summary.json", "w"), indent=1)
    with open(out / "SHA256SUMS", "w") as fh:
        for p in sorted(out.glob("*")):
            if p.name != "SHA256SUMS" and p.is_file():
                fh.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "energy_grid"}, indent=1))


if __name__ == "__main__":
    main()
