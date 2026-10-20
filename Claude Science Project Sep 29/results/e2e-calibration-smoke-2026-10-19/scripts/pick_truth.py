"""Truth draw for one calibration case (protocol 3.1, 3.3). Reads the fuel-only single-particle replicates of truth_core.sh.
Candidate (replicate r, stratum s) has weight exp(log_evidence_by_mode[s]) (uniform stratum prior; the evidence carries every
proposal correction and the fuel record). For each candidate the state at every logged epoch comes from the residual snapshots
(1 particle per stratum, tempering off, so the snapshot IS the path); predicted BTO = table value - engine residual; predicted BFO
(without bias) = numpy port of satcom::bfo_without_bias_hz with the vertical rate from the +1 s dummy epoch.
Synthetic cruise data: BTO = pred + N(0, sd); BFO = pred + b + N(0, sd), b ~ N(150, 25) (constant: run J has bias drift OFF).
Usage: pick_truth.py CASE_DIR SEED OBS_CSV EPH_CSV [--south-event HZ]  -> CASE_DIR/truth-core.json"""
import sys, json, glob, os, math, tomllib, pathlib
import numpy as np
from e2e_common import read_rows, sat_state, bto_us, bfo_nobias

NAMES = ["LateralNavigation", "MagneticHeading", "MagneticTrack", "TrueHeading", "TrueTrack"]


def stop_header(p):
    txt = open(p).read(); head = txt.split("[lookahead]")[0] if "[lookahead]" in txt else txt.split("[[row]]")[0]
    return tomllib.loads(head)["stop"]


def main():
    cd, seed, obs_csv, eph_csv = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    ev = sys.argv[sys.argv.index("--event") + 1] if "--event" in sys.argv else None   # e.g. m0011.bto:17540:18540,m0011.bfo:202:302
    ev = [(t.split(":")[0].split(".")[0], t.split(":")[0].split(".")[1], float(t.split(":")[1]), float(t.split(":")[2])) for t in ev.split(",")] if ev else None
    rng = np.random.default_rng(seed)
    O = {r["epoch_id"]: r for r in read_rows(obs_csv)}; EP = read_rows(eph_csv)
    ep_ids = [e for e in O if not e.startswith("m0019")]
    cands = []
    for sd in sorted(glob.glob(f"{cd}/truth-core/prior/seed-*")):
        st = stop_header(f"{sd}/handoff-m0011/handoff.toml"); lz = st["log_evidence_by_mode"]
        H = np.load(f"{sd}/handoff-m0011/handoff.npy")
        for s, name in enumerate(NAMES):
            if lz[s] < -1e5: continue                       # fuel hard reject: the path contradicts the fuel record
            snap = {}
            ok = True
            for e in ep_ids + [q + e for e in ep_ids if "bfo" in O[e]["cruise"].split() for q in ("w", "x")]:
                f = f"{sd}/residuals/{name}-{e}.npy"
                if not os.path.exists(f): ok = False; break
                snap[e] = np.load(f)[0].astype(np.float64)
            if not ok: continue
            # the hand-off row of this stratum: match by position at m0011 (rows are copies of the single particle)
            m11 = snap["m0011"]; d = np.hypot(H[:, 1] - m11[0], H[:, 2] - m11[1]); j = int(np.argmin(d))
            if d[j] > 1e-4: continue
            cands.append(dict(seed_dir=sd, stratum=s, name=name, log_w=float(lz[s]), row=j, snap=snap, handoff=H[j].tolist()))
    if not cands: sys.exit("no candidate survived the fuel record")
    lw = np.array([c["log_w"] for c in cands]); w = np.exp(lw - lw.max()); w /= w.sum()
    ess = 1 / np.sum(w ** 2)
    b = rng.normal(150.0, 25.0, len(cands))
    syn_all = []
    for k, c in enumerate(cands):
        rows = {}
        for e in ep_ids:
            r = O[e]; s = c["snap"][e]; lat, lon, alt, gs, trk = s[0], s[1], s[2], s[3], s[4]
            out = {"lat": lat, "lon": lon, "alt_ft": alt, "gs_kt": gs, "track_deg": trk}
            if r["bto_us"]:
                out["bto_pred"] = float(r["bto_us"]) - s[7]
                sat, satv = sat_state(EP, e); out["bto_pred_port"] = bto_us(sat, lat, lon, alt)
                out["bto_syn"] = out["bto_pred"] + rng.normal(0, float(r["bto_sd_us"]))
            if "bfo" in r["cruise"].split():
                fwd = (c["snap"]["x" + e][2] - alt) * 60.0; bwd = (alt - c["snap"]["w" + e][2]) * 60.0
                # engine reports the instantaneous rate: 0 if a level segment touches t, else the full segment rate
                vup = 0.0 if (abs(fwd) < 1 or abs(bwd) < 1) else (fwd if abs(fwd) >= abs(bwd) else bwd)
                sat, satv = sat_state(EP, e); vn, ve = gs * math.cos(math.radians(trk)), gs * math.sin(math.radians(trk))
                out["vup_fpm"] = vup; out["bfo_pred"] = bfo_nobias(sat, satv, float(r["satellite_afc_hz"]), lat, lon, alt, vn, ve, vup)
                out["bfo_syn"] = out["bfo_pred"] + b[k] + rng.normal(0, float(r["bfo_sd_hz"]))
            rows[e] = out
        syn_all.append(rows)
    keep = np.ones(len(cands), bool)
    if ev is not None:
        keep = np.array([all(lo <= s[e][q + "_syn"] <= hi for e, q, lo, hi in ev) for s in syn_all])
    if not keep.any(): sys.exit("no candidate meets the data event")
    wk = np.where(keep, w, 0.0); wk /= wk.sum(); k = int(rng.choice(len(cands), p=wk))
    c = cands[k]
    res = dict(case_seed=seed, n_candidates=len(cands), candidate_ess=float(ess), data_event=sys.argv[sys.argv.index("--event") + 1] if ev else None, n_accepted=int(keep.sum()), accepted_ess=float(1 / np.sum((w[keep] / w[keep].sum()) ** 2)),
               event_rate_weighted=float(w[keep].sum()), chosen=dict(seed_dir=c["seed_dir"], stratum=c["stratum"], name=c["name"], row=c["row"], log_w=c["log_w"]),
               bias_hz=float(b[k]), epochs=syn_all[k], handoff_row=c["handoff"],
               port_check_bto_max_abs_us=float(max(abs(v["bto_pred"] - v["bto_pred_port"]) for v in syn_all[k].values() if "bto_pred" in v)),
               candidate_m0011=[[float(s["m0011"]["lat"]), float(s["m0011"]["lon"]), float(s["m0011"]["bfo_syn"]), float(s["m0011"]["bto_syn"]), float(wi), int(kp)] for s, wi, kp in zip(syn_all, w, keep)])
    json.dump(res, open(f"{cd}/truth-core.json", "w"), indent=1)
    print(json.dumps({k_: v for k_, v in res.items() if k_ not in ("epochs", "handoff_row", "candidate_m0011")}))
    print("truth at m0011:", {k_: round(v, 3) for k_, v in res["epochs"]["m0011"].items()})


if __name__ == "__main__":
    main()
