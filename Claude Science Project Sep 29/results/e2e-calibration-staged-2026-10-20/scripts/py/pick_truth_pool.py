"""A1/A2 candidate flights for one calibration case from the shared pool (protocol 3.1, 3.3; amendments A1, A2, S2 fix).
Candidate (pool replicate, stratum) has weight exp(log_evidence_by_mode) (fuel-only prior). With the case seed this draws
the constant BFO bias b ~ N(150, 25) per candidate and the measurement noise per epoch, applies the DATA-ONLY acceptance event
to the synthetic data, and writes the accepted set, resampled to at most MAXC distinct candidates with weights kept, to
CASE_DIR/truth-candidates.json. The flight itself is chosen by pick_flight.py after the end-of-flight stage has flown every
candidate, with weight x Z(parent) (S2). Usage: pick_truth_pool.py CASE_DIR SEED POOL_DIR OBS_CSV --event SPEC [--max-candidates 400]"""
import sys, json, glob
import numpy as np
from e2e_common import read_rows

NAMES = ["LateralNavigation", "MagneticHeading", "MagneticTrack", "TrueHeading", "TrueTrack"]


def main():
    cd, seed, pool, obs_csv = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    evs = sys.argv[sys.argv.index("--event") + 1]
    ev = [(t.split(":")[0].split(".")[0], t.split(":")[0].split(".")[1], float(t.split(":")[1]), float(t.split(":")[2])) for t in evs.split(",")]
    maxc = int(sys.argv[sys.argv.index("--max-candidates") + 1]) if "--max-candidates" in sys.argv else 400
    rng = np.random.default_rng(seed)
    O = {r["epoch_id"]: r for r in read_rows(obs_csv)}
    files = sorted(glob.glob(f"{pool}/chunk-*.npz"))
    Z = [np.load(f) for f in files]; ep_ids = list(Z[0]["ep_ids"])
    cat = lambda k: np.concatenate([z[k] for z in Z])
    P = {k: cat(k) for k in ("seed", "stratum", "row", "log_w", "H", "state", "bto_pred", "bfo_pred", "vup", "chunk_tar")}
    N = len(P["seed"]); lw = P["log_w"]; w = np.exp(lw - lw.max()); w /= w.sum(); ess = float(1 / np.sum(w ** 2))
    b = rng.normal(150.0, 25.0, N)
    bto_syn = np.full_like(P["bto_pred"], np.nan); bfo_syn = np.full_like(P["bfo_pred"], np.nan)
    for i, e in enumerate(ep_ids):
        r = O[e]
        if r["bto_us"]: bto_syn[:, i] = P["bto_pred"][:, i] + rng.normal(0, float(r["bto_sd_us"]), N)
        if "bfo" in r["cruise"].split(): bfo_syn[:, i] = P["bfo_pred"][:, i] + b + rng.normal(0, float(r["bfo_sd_hz"]), N)
    keep = np.ones(N, bool)
    for e, q, lo, hi in ev:
        i = ep_ids.index(e); x = bto_syn[:, i] if q == "bto" else bfo_syn[:, i]
        keep &= np.isfinite(x) & (x >= lo) & (x <= hi)
    if not keep.any(): sys.exit("no candidate meets the data event")
    wk = np.where(keep, w, 0.0); rate = float(wk.sum()); wk /= wk.sum(); acc_ess = float(1 / np.sum(wk ** 2))
    idx = np.flatnonzero(keep)
    if len(idx) <= maxc:
        sel, wt = idx, wk[idx]; resampled = False
    else:                                                     # systematic resampling to maxc draws; multiplicity becomes the weight
        u = (rng.random() + np.arange(maxc)) / maxc; cs = np.cumsum(wk); pick = np.searchsorted(cs, u)
        sel, cnt = np.unique(pick, return_counts=True); wt = cnt / maxc; resampled = True
    cands = []
    for k, wtk in zip(sel, wt):
        epochs = {}
        for i, e in enumerate(ep_ids):
            r = O[e]; st = P["state"][k, i]
            d = {"lat": float(st[0]), "lon": float(st[1]), "alt_ft": float(st[2]), "gs_kt": float(st[3]), "track_deg": float(st[4])}
            if r["bto_us"]: d["bto_pred"] = float(P["bto_pred"][k, i]); d["bto_syn"] = float(bto_syn[k, i])
            if "bfo" in r["cruise"].split(): d["vup_fpm"] = float(P["vup"][k, i]); d["bfo_pred"] = float(P["bfo_pred"][k, i]); d["bfo_syn"] = float(bfo_syn[k, i])
            epochs[e] = d
        cands.append(dict(seed=int(P["seed"][k]), seed_dir=f"{cd}/truth-handoff/seed-{int(P['seed'][k])}", chunk_tar=str(P["chunk_tar"][k]), stratum=int(P["stratum"][k]), name=NAMES[int(P["stratum"][k])],
                          row=int(P["row"][k]), log_w=float(lw[k]), wt=float(wtk), bias_hz=float(b[k]), epochs=epochs, handoff_row=P["H"][k].tolist()))
    res = dict(case_seed=seed, pool=pool, pool_chunks=len(files), n_candidates=N, candidate_ess=ess, data_event=evs, n_accepted=int(keep.sum()),
               accepted_ess=acc_ess, event_rate_weighted=rate, max_candidates=maxc, resampled=resampled, n_flown=len(cands), candidates=cands)
    json.dump(res, open(f"{cd}/truth-candidates.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "candidates"}))


if __name__ == "__main__":
    main()
