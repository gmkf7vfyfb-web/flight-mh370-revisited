"""Drift-surface sensitivity of a composed product, by exact re-weighting of the composer's row weights.

The composer publishes per-row weights w_G (one f32 per impacts32 row; value = W_Q(stratum) x pooled within-stratum weight).
G = base x L_drift_eff x (other factors), where L_drift_eff = exp(lnL) on scored rows and, on unscored rows, the carry value
D = sum_c w_base L / sum_c w_base over the seed's scored rows (compose lib.rs, ruling 1). This script divides out the drift
factor actually used (glorys12 h50), multiplies in an alternative drift surface with its own carry value, re-pools within
each stratum and restores the stratum weight W_Q. With the alternative equal to the original it returns w_G exactly.

Alternative surfaces: the two independent particle halves of the h50 surface (ln_l_half_a / ln_l_half_b; the drift
transport Monte Carlo noise, which a seed split-half cannot see because every seed uses the same surface), the bandwidths
25 / 100 / 200 km, and GlobCurrent as run (F1 windage bias; illustration only).

Statistics per surface: weighted median and 2.5 / 97.5 % impact latitude (0.005 deg histogram), the share of weight
inside 33-36 S, the unscored-row weight share, and ln E_G[L_P] (Pleiades factor given H, lnL_pleiades_glorys12) whose
difference from the original surface is the change in ln R (the P1 term of ln R does not depend on drift).

Usage: python surface_sensitivity.py <drift runs dir> <exchange dir> <end of flight smoke dir> <out.csv> [--products ...]
"""
import argparse
import json
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from score_impacts import lookup, surface_arrays  # noqa: E402

STRATA = ["next-c-free", "next-c-repro-radar", "next-c-descent-climb", "next-c-routes"]
HALVES = {"glorys12_h50_half_a": "ln_l_half_a", "glorys12_h50_half_b": "ln_l_half_b"}
EXPORTED = ["glorys12_h50", "glorys12_h25", "glorys12_h100", "glorys12_h200", "globcurrent_h50"]
EDGES = np.arange(-50.0, 0.0 + 1e-9, 0.005)


def lse(x):
    m = np.max(x)
    return m + np.log(np.sum(np.exp(x - m))) if np.isfinite(m) else -np.inf


def quant(h, q):
    c = np.cumsum(h) / h.sum()
    return float(np.interp(q, c, EDGES[1:]))


def main(runs, exch, recipe, out, products, seeds):
    sys.path.insert(0, recipe)
    from compact_impacts import load as load_compact  # end of flight's reader, read-only
    halfsurf = {k: surface_arrays(os.path.join(runs, "debris-drift-production-glorys12/merged"), c) for k, c in HALVES.items()}
    surfaces = EXPORTED + list(HALVES)
    ex = pathlib.Path(exch)
    rw = ex / "composer/next-run-c/row-weights"
    res = {p: {s: {"hist": np.zeros(EDGES.size - 1), "lp": [], "nc": 0.0, "band": 0.0, "tot": 0.0} for s in surfaces} for p in products}
    wq = {p: json.loads((rw / p / "manifest.json").read_text())["stratum_weights"] for p in products}
    per_stratum = []
    for st in STRATA:
        # per stratum: log base weight + per-surface log factor per row, accumulated over seeds, then normalised to W_Q
        acc = {p: {s: [] for s in surfaces} for p in products}
        for k in seeds:
            d = ex / "end-of-flight/next-run-c" / st / f"seed-{k}"
            _, gcol = load_compact(d)
            lat, lon = gcol("latitude_deg"), gcol("longitude_deg")
            D = np.load(ex / "debris-drift/next-run-c" / st / f"seed-{k}" / "drift-lnL.npy", mmap_mode="r")
            Q = np.load(ex / "pleiades/hydro-test/next-run-c" / st / f"seed-{k}" / "pleiades-lnL.npy", mmap_mode="r")
            assert len(D) == lat.size == len(Q)
            lp = np.asarray(Q["lnL_pleiades_glorys12"], float)
            bad = ~np.isfinite(lp)
            if bad.any():  # Pleiades not computed on a few rows: carried at its own seed mean (per-factor carry)
                lp[bad] = lse(lp[~bad]) - np.log((~bad).sum())
            alt = {}
            for s in EXPORTED:
                m, b = s.split("_")
                alt[s] = (np.asarray(D[f"state_{m}_{b}"]) == 1, np.asarray(D[f"lnL_{m}_{b}"], float))
            for s, sa in halfsurf.items():
                flag, ll = lookup(*sa, lat, lon)
                alt[s] = (flag == 1, ll)
            ok0, l0 = alt["glorys12_h50"]
            for p in products:
                w = np.fromfile(rw / p / st / f"seed-{k}.f32", dtype=np.float32).astype(float)
                assert w.size == lat.size
                pos = w > 0
                lw = np.full(w.size, -np.inf)
                lw[pos] = np.log(w[pos])
                # undo the original drift factor: scored rows divide by L, unscored by the seed's carry value D0
                lb = lw.copy()
                lb[ok0] -= l0[ok0]
                ln_d0 = lse(lb[ok0] + l0[ok0]) - lse(lb[ok0])
                lb[~ok0] -= ln_d0
                for s in surfaces:
                    ok, l = alt[s]
                    lf = np.empty(w.size)
                    lf[ok] = l[ok]
                    lf[~ok] = lse(lb[ok] + l[ok]) - lse(lb[ok])
                    acc[p][s].append((lb + lf, lat, lp, ok))
                # composer's joint carry on the original surface: an unscored-drift row carries the joint mean of the
                # scored rows, so in H its own Pleiades value is replaced by the scored rows' weighted mean
                jc = lp.copy()
                jc[~ok0] = lse(lw[ok0] + lp[ok0]) - lse(lw[ok0])
                acc[p].setdefault("_joint", []).append((lw, jc))
        for p in products:
            lwj = acc[p].pop("_joint")
            totj = lse(np.concatenate([a[0] for a in lwj]))
            per_stratum.append((p, st, "glorys12_h50_joint_carry", lse(np.array([lse(a[0] + a[1]) for a in lwj])) - totj))
            for s in surfaces:
                tots = lse(np.concatenate([a[0] for a in acc[p][s]]))
                per_stratum.append((p, st, s, lse(np.array([lse(a[0] + a[2]) for a in acc[p][s]])) - tots))
            for s in surfaces:
                tot = lse(np.concatenate([a[0] for a in acc[p][s]]))
                for lwn, la, lp, ok in acc[p][s]:
                    wn = np.exp(lwn - tot) * wq[p][st]
                    r = res[p][s]
                    r["hist"] += np.histogram(la, bins=EDGES, weights=wn)[0]
                    sel = wn > 0
                    r["lp"].append(lse(np.log(wn[sel]) + lp[sel]))
                    r["nc"] += wn[~ok].sum()
                    r["band"] += wn[(la >= -36.0) & (la <= -33.0)].sum()
                    r["tot"] += wn.sum()
            acc[p] = None
        print(f"{st}: done", flush=True)
    rows = []
    for p in products:
        base = None
        for s in surfaces:
            r = res[p][s]
            lnE = lse(np.array(r["lp"])) - np.log(r["tot"])
            if s == "glorys12_h50":
                base = lnE
            rows.append((p, s, quant(r["hist"], 0.5), quant(r["hist"], 0.025), quant(r["hist"], 0.975), r["band"] / r["tot"], r["nc"] / r["tot"], lnE, r["tot"]))
    with open(out, "w") as f:
        f.write("product,surface,median_lat,lat_2p5,lat_97p5,share_33_36S,unscored_share,ln_E_G_LP,dlnR_vs_glorys12_h50,total_weight\n")
        for p, s, md, lo, hi, band, nc, lnE, tot in rows:
            b = [x for x in rows if x[0] == p and x[1] == "glorys12_h50"][0][7]
            f.write(f"{p},{s},{md:.3f},{lo:.3f},{hi:.3f},{band:.4f},{nc:.4f},{lnE:.4f},{lnE - b:+.4f},{tot:.6f}\n")
    with open(out.replace(".csv", "-per-stratum.csv"), "w") as f:
        f.write("product,stratum,surface,ln_E_G_LP\n")
        for p, st, s, v in per_stratum:
            f.write(f"{p},{st},{s},{v:.4f}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs"); ap.add_argument("exch"); ap.add_argument("recipe"); ap.add_argument("out")
    ap.add_argument("--products", default="r600-bto+unpowered-G,heldout+unpowered-G")
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8")
    a = ap.parse_args()
    main(a.runs, a.exch, a.recipe, a.out, a.products.split(","), [int(x) for x in a.seeds.split(",")])
