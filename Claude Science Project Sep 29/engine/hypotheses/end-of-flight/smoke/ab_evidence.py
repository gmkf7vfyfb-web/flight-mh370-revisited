"""22:41 A-vs-B evidence: for each option column (loglik:*) of two terminal runs from the SAME 22:41 hand-off, ln Z per arm
(ln sum w L - ln sum w), ln BF(A:B) = ln Z_A - ln Z_B, effective parents and impacts, and per-arm posterior median latitude.
Usage: python ab_evidence.py RUN_A RUN_B OUT_JSON [seed]
       python ab_evidence.py slim RUN SEED      -> RUN/bto-bfo/seed-SEED/slim.npz (float32/float64 subset), then the caller may delete impacts.npy
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp


def load(run, seed):
    run = pathlib.Path(run); m = json.loads((run / "run.json").read_text()); c = {k: i for i, k in enumerate(m["impact_columns"])}
    X = np.load(run / "bto-bfo" / f"seed-{seed}" / "impacts.npy", mmap_mode="r")
    return m, c, (lambda k: np.asarray(X[:, c[k]], float))


def stats(c, g):
    w = g("weight"); lw = np.log(w) - np.log(w.sum()); par = g("parent").astype(np.int64); lat = g("latitude_deg")
    out = {}
    for k in [k for k in c if k.startswith("loglik:")]:
        ll = g(k); ll = np.where(np.isfinite(ll), ll, -np.inf)
        lz = float(logsumexp(lw + ll)); p = np.exp(lw + ll - lz); P = np.bincount(par, weights=p)
        o = np.argsort(lat); cw = np.cumsum(p[o])
        out[k[7:]] = {"ln_Z": lz, "eff_parents": float(1 / (P ** 2).sum()), "eff_impacts": float(1 / (p ** 2).sum()),
                      "median_lat": float(lat[o][np.searchsorted(cw, 0.5)])}
    return out


def main(a, b, outp, seed="1"):
    (ma, ca, ga), (mb, cb, gb) = load(a, seed), load(b, seed)
    A, B = stats(ca, ga), stats(cb, gb)
    res = {"run_A": str(a), "run_B": str(b), "seed": seed, "options": {}}
    for k in A:
        if k in B:
            res["options"][k] = {"A": A[k], "B": B[k], "ln_BF_A_to_B": A[k]["ln_Z"] - B[k]["ln_Z"]}
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))
    for k, v in res["options"].items():
        print(f"{k:28s} lnZ A {v['A']['ln_Z']:8.3f} (eff par {v['A']['eff_parents']:8.1f})  B {v['B']['ln_Z']:8.3f} (eff par {v['B']['eff_parents']:8.1f})"
              f"  ln BF A:B {v['ln_BF_A_to_B']:+.2f}  median lat A {v['A']['median_lat']:.2f} B {v['B']['median_lat']:.2f}")


SLIM = ["weight", "parent", "unix_s", "latitude_deg", "longitude_deg", "latent:onset_mechanism", "latent:control_realised",
        "latent:recovery_attempted", "latent:residual_bank_sign", "latent:realised_flameout_unix_s"]


def slim(run, seed):
    m, c, g = load(run, seed)
    keep = SLIM + [k for k in c if k.startswith("loglik:")]
    arrs = {k: (g(k) if k in ("unix_s", "latent:realised_flameout_unix_s", "weight") else g(k).astype(np.float32)) for k in keep if k in c}
    np.savez(pathlib.Path(run) / "bto-bfo" / f"seed-{seed}" / "slim.npz", **arrs)
    m2 = m["impact_columns"]; assert all(k in m2 for k in arrs)


if __name__ == "__main__":
    if sys.argv[1] == "slim":
        slim(sys.argv[2], sys.argv[3])
    else:
        main(*sys.argv[1:])
