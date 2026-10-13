"""Stand-in (architecture, 11 Oct 2026) companion to end of flight's smoke/ab_evidence.py. Does NOT replace it: ab_evidence.py
runs unchanged first. This adds, from the same two impacts.npy files, (1) the derived option 'm0011+r600-bto' (00:19 R600 BTO
Only) built with end of flight's OWN derived_logliks (smoke/displacement_hist.py, imported read-only): loglik:m0011 + the core
Gaussian BTO term at m0019a; (2) the '~v212' version (contact speed |v| > 212 m/s removed, normalised by the UNFILTERED total, as
Pleiades' branch_eof289.py); (3) per-arm family shares with end of flight's own family_labels (smoke/compact_impacts.py);
(4) a mini npz (float32) so impacts.npy can be deleted (disk). Usage: python standin_ab_summary.py RUN_A RUN_B SEED OUT_JSON EOF_SMOKE_DIR"""
import json, sys, pathlib, importlib.util
import numpy as np
from scipy.special import logsumexp

runA, runB, seed, outp, smoke = sys.argv[1:6]
smoke = pathlib.Path(smoke)
def mod(name):
    spec = importlib.util.spec_from_file_location("eof_" + name, smoke / f"{name}.py"); m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(smoke)); spec.loader.exec_module(m); return m
DH, CI = mod("displacement_hist"), mod("compact_impacts")

def load(run):
    run = pathlib.Path(run); m = json.loads((run / "run.json").read_text()); c = {k: i for i, k in enumerate(m["impact_columns"])}
    X = np.load(run / "bto-bfo" / f"seed-{seed}" / "impacts.npy", mmap_mode="r")
    return m, c, (lambda k: np.asarray(X[:, c[k]], float)), X.shape[0]

def arm(run):
    m, c, g, n = load(run)
    w = g("weight"); W = w.sum(); lw = np.log(w) - np.log(W); par = g("parent").astype(np.int64); lat = g("latitude_deg"); lon = g("longitude_deg")
    spd = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    present = [k[7:] for k in c if k.startswith("loglik:")]
    der = DH.derived_logliks(m, g, present)          # {'r600-bto': BTO term, 'both-bto': ...}; EoF's own code
    opts = {k: g("loglik:" + k) for k in present}
    if "r600-bto" in der:
        opts["m0011+r600-bto"] = opts["m0011"] + der["r600-bto"]
    fl = CI.family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))
    fam = fl["family_code"]
    out = {}
    for k, ll in opts.items():
        ll = np.where(np.isfinite(ll), ll, -np.inf)
        for ver, keep in (("all", np.ones(n, bool)), ("~v212", spd <= 212.0)):
            a = np.where(keep, lw + ll, -np.inf)
            if not np.isfinite(a).any():
                out[f"{k}{'' if ver=='all' else ver}"] = None; continue
            lz = float(logsumexp(a)); p = np.exp(a - lz); P = np.bincount(par, weights=p)
            o = np.argsort(lat); cw = np.cumsum(p[o])
            fs = {str(int(f)): float(p[fam == f].sum()) for f in (1, 2, 4, 3, 5, 6)}
            out[f"{k}{'' if ver=='all' else ver}"] = {"ln_Z": lz, "eff_parents": float(1 / (P ** 2).sum()), "eff_impacts": float(1 / (p ** 2).sum()),
                "median_lat": float(lat[o][np.searchsorted(cw, 0.5)]), "family_share": fs,
                "removed_share_v212": float(1 - np.exp(logsumexp(np.where(keep, lw + ll, -np.inf)) - logsumexp(lw + ll))) if ver != "all" else 0.0}
    prior_fam = {str(int(f)): float(np.exp(lw)[fam == f].sum()) for f in (1, 2, 4, 3, 5, 6)}
    mini = {"lw": lw.astype(np.float32), "parent": par.astype(np.int32), "lat": lat.astype(np.float32), "lon": lon.astype(np.float32),
            "speed": spd.astype(np.float32), "family_code": np.nan_to_num(fam, nan=0).astype(np.int8)}
    for k in ("m0011", "m0011+r600-bto", "m0011+r600/no-offset", "m0011+r600/inflated", "m0011+r600/startup-offset", "m2315-bfo"):
        if k in opts: mini["ll:" + k] = np.where(np.isfinite(opts[k]), opts[k], -np.inf).astype(np.float32)
    np.savez(pathlib.Path(run) / "bto-bfo" / f"seed-{seed}" / "mini.npz", **mini)
    return {"n_impacts": int(n), "sum_weight": float(W), "prior_family_share": prior_fam, "options": out,
            "code_revision": m.get("code_revision"), "config_paths": m.get("config_paths")}

A, B = arm(runA), arm(runB)
res = {"run_A": runA, "run_B": runB, "seed": seed, "A": A, "B": B, "ln_BF_A_to_B": {}}
for k in A["options"]:
    if A["options"][k] and B["options"].get(k):
        res["ln_BF_A_to_B"][k] = A["options"][k]["ln_Z"] - B["options"][k]["ln_Z"]
pathlib.Path(outp).write_text(json.dumps(res, indent=1))
for k in ("m0011", "m0011+r600-bto", "m0011+r600/no-offset", "m0011+r600/inflated", "m0011~v212", "m0011+r600-bto~v212", "m0011+r600/no-offset~v212"):
    if k in res["ln_BF_A_to_B"]:
        print(f"  {k:28s} lnBF A:B {res['ln_BF_A_to_B'][k]:+.2f}  eff par A {A['options'][k]['eff_parents']:8.1f} B {B['options'][k]['eff_parents']:8.1f}")
