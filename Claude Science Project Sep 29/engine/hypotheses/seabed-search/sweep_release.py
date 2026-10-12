"""Every labelled sensitivity of this module on one end-of-flight release, in ONE evaluate pass.

Why one pass. `mh370 evaluate` reports `covered_fraction_<campaign>` as the RAW raster coverage
c_k(y) (lib.rs `predict`), and the likelihood is built from those alone:

    detectable miss  M(y) = prod_k [1 - c_k(y) g_k q_k^eff],     q_k^eff = detection_probability x coverage_fraction
    shared           P(no find | y) = rho + (1 - rho) M(y)
    independent      P(no find | y) = prod_k [rho + (1 - rho)(1 - c_k(y) g_k q_k^eff)]

For a point target g_k = 1. So once the eight coverage layers (the Phase 2 union, its four sensor
layers, Bluefin-21, Ocean Infinity 2018 and 2025-26) have been rastered ONCE per impact, every
scenario in `report.scenarios` - the rho sweep, the q sweep, the OI variants, the repeat-search
split under either dependence, and each campaign alone and cumulatively - is exact algebra on those
columns. Re-running evaluate per scenario would raster the same eight layers 20 times over.

The base scenario is checked against evaluate's own `no_find_probability` column, so the algebra is
verified against the Rust on every seed rather than trusted.

  python hypotheses/seabed-search/sweep_release.py <spec> <out.json> [--constraints alive]

<spec> is `runs/<dir>:<weight>,...` exactly as impact_map_options.py takes it.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BINARY = ROOT / "target" / "release" / "mh370"
sys.path.insert(0, str(ROOT / "hypotheses" / "end-of-flight" / "smoke"))
sys.path.insert(0, str(ROOT / "hypotheses" / "pleiades" / "prepare"))
sys.path.insert(0, str(HERE))
from displacement_hist import option_posteriors  # noqa: E402
import compact_eval as ce  # noqa: E402
import report as rp  # noqa: E402

RHO_SWEEP = rp.RHO_SWEEP
ESS_FLOOR = 1000.0

# The eight layers, rastered once. q_eff and coverage_fraction come from the module's own TOMLs.
LAYERS = [
    ("phase2-2014-2017", "phase2", 0.945, 1.0),
    ("phase2-deep-tow", "phase2-deep-tow", 0.945, 1.0),
    ("phase2-go-phoenix", "phase2-go-phoenix", 0.945, 1.0),
    ("phase2-dhj", "phase2-dhj", 0.945, 1.0),
    ("phase2-auv", "phase2-auv", 0.945, 1.0),
    ("bluefin-2014", "bluefin-2014", 0.9, 1.0),
    ("ocean-infinity-2018", "ocean-infinity-2018", 0.9, 0.889),
    ("ocean-infinity-2025", "ocean-infinity-2025", 0.9, 0.7808),
]
BASE = ["phase2-2014-2017", "bluefin-2014"]
SPLIT = ["phase2-deep-tow", "phase2-go-phoenix", "phase2-dhj", "phase2-auv", "bluefin-2014"]


def all_layers_toml():
    """run.toml override listing all eight layers, so one evaluate rasters them together."""
    lines = []
    for name, layer, q, cf in LAYERS:
        lines.append("[[hypotheses.seabed-search.campaigns]]")
        lines.append(f'name = "{name}"')
        if (HERE / "coverage" / f"{layer}.cov").exists() and layer.startswith("ocean-infinity"):
            lines.append(f'layer_file = "hypotheses/seabed-search/coverage/{layer}.cov"')
        else:
            lines.append(f'layer = "{layer}"')
        lines.append(f"detection_probability = {q}")
        if cf != 1.0:
            lines.append(f"coverage_fraction = {cf}")
    return "\n".join(lines) + "\n"


def p_no_find(cov, names, rho, qeff, dependence="shared"):
    """P(no find) per impact from the raw coverage columns, point target."""
    if dependence == "shared":
        m = np.ones(len(next(iter(cov.values()))))
        for n in names:
            m = m * (1.0 - cov[n] * qeff[n])
        return rho + (1.0 - rho) * m
    p = np.ones(len(next(iter(cov.values()))))
    for n in names:
        p = p * (rho + (1.0 - rho) * (1.0 - cov[n] * qeff[n]))
    return p


def scenarios():
    """(label, kind, names, rho, qeff overrides, dependence). Mirrors report.scenarios."""
    q0 = {n: q * cf for n, _, q, cf in LAYERS}
    out = [("run.toml", "main", BASE, 0.05, {}, "shared")]
    out += [(f"rho {r:g}", "rho", BASE, r, {}, "shared") for r in RHO_SWEEP if r != 0.05]
    for q in (0.90, 0.98):
        out.append((f"Phase 2 q {q:.2f}", "q", BASE, 0.05, {"phase2-2014-2017": q}, "shared"))
    out.append(("Phase 2 split, shared misses", "repeat", SPLIT, 0.05, {}, "shared"))
    out.append(("Phase 2 split, independent misses", "repeat", SPLIT, 0.05, {}, "independent"))
    out.append(("+ OI 2025-26 inferred, outboard band only", "oi25",
                BASE + ["ocean-infinity-2025"], 0.05, {}, "shared"))
    out.append(("+ OI 2018 inferred, coverage 0.889", "oi",
                BASE + ["ocean-infinity-2018"], 0.05, {}, "shared"))
    out.append(("+ OI 2018 inferred, coverage 0.952", "oi", BASE + ["ocean-infinity-2018"], 0.05,
                {"ocean-infinity-2018": 0.9 * 0.952}, "shared"))
    order = ["bluefin-2014", "phase2-2014-2017", "ocean-infinity-2018"]
    for k, c in enumerate(order):
        out.append((f"alone: {c}", "alone", [c], 0.0, {}, "shared"))
        out.append((f"adding, in order: {c}", "cumulative", order[:k + 1], 0.0, {}, "shared"))
    return [(lab, kind, names, rho, dict(q0, **ovr), dep) for lab, kind, names, rho, ovr, dep in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="runs/<dir>:<weight>,... as impact_map_options.py takes it")
    ap.add_argument("out", type=pathlib.Path)
    ap.add_argument("--constraints", default="alive")
    a = ap.parse_args()

    parts = []
    for part in a.spec.split(","):
        d, _, w = part.partition(":")
        parts.append((pathlib.Path(d), float(w) if w else 1.0))
    tw = sum(w for _, w in parts)
    parts = [(d, w / tw) for d, w in parts]
    cons = tuple(x for x in a.constraints.split(",") if x)
    scratch = ROOT / "runs" / "seabed-search-analysis" / "scratch-sweep"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "all-layers.toml").write_text(all_layers_toml())
    scen = scenarios()

    acc, half = {}, {}
    for d, wfam in parts:
        seeds = sorted((d / "bto-bfo").glob("seed-*"))
        share = wfam / len(seeds)
        # Split-half on POSITION in this stratum's seed list, not on the seed number. A release
        # need not have eight seeds (run D-he has four, with seed-5..8 present but empty), and a
        # hard "seed number <= 4" test then puts every seed in one half and reports a split-half
        # against nothing.
        half_of = {s: (0 if i < len(seeds) // 2 else 1) for i, s in enumerate(seeds)}
        for sd in seeds:
            tmp = None
            try:
                src = sd / "impacts.npy"
                if ce.is_compact(sd):
                    tmp = scratch / f"compact-{d.name}-{sd.name}"
                    src = ce.eval_input(sd, tmp)
                out = scratch / f"evaluate-{d.name}-{sd.name}"
                subprocess.run([str(BINARY), "evaluate", str(HERE / "run.toml"),
                                str(scratch / "all-layers.toml"), str(src), str(out)],
                               check=True, capture_output=True, cwd=ROOT)
            finally:
                if tmp is not None:
                    shutil.rmtree(tmp, ignore_errors=True)
            cols = json.loads((out / "evaluate.json").read_text())["columns"]
            V = np.load(out / "evaluate.npy")
            idx = {c: i for i, c in enumerate(cols)}
            cov = {n: V[:, idx[f"seabed-search:covered_fraction_{n}"]].astype(np.float64)
                   for n, _, _, _ in LAYERS}
            rust = V[:, idx["seabed-search:no_find_probability"]].astype(np.float64)
            shutil.rmtree(out, ignore_errors=True)

            # Check the algebra against the Rust on every seed. run.toml's own two campaigns are a
            # SUBSET of the eight evaluated here, so rust is the eight-campaign value; rebuild that.
            allp = p_no_find(cov, [n for n, _, _, _ in LAYERS], 0.05,
                             {n: q * cf for n, _, q, cf in LAYERS}, "shared")
            bad = float(np.abs(allp - rust).max())
            if bad > 1e-12:
                sys.exit(f"{sd}: the algebra does not reproduce evaluate (max |delta| {bad:.3e})")

            # Survival factor (architecture 20:55Z 11 Oct): "no in-flight breakup before 00:19:37"
            # is part of the 00:19 data model, and PRIMARY results carry (1 - P). End of flight
            # ships it as its own column, not folded into `weight`, and `option_posteriors` does
            # not apply it, so both arms are computed here and both are labelled.
            names, g, _ = ce.seed_reader(sd)
            SURV = "latent:inflight_p_breakup_to_m0019b"
            surv = (1.0 - g(SURV)) if SURV in names else None

            post = list(option_posteriors(d, sd, constraints=cons))
            for key, p, c in post:
                on_p2 = cov["phase2-2014-2017"]
                arms = [("without survival factor", p)]
                if surv is not None:
                    q = p * surv
                    tot = float(q.sum())
                    if tot > 0:
                        arms.insert(0, ("primary", q / tot))
                for arm, pw in arms:
                  for lab, kind, nm, rho, qeff, dep in scen:
                    P = p_no_find(cov, nm, rho, qeff, dep)
                    z = float((pw * P).sum())
                    k = (key, lab, arm)
                    s = acc.setdefault(k, {"z": 0.0, "kind": kind, "on_before": 0.0,
                                           "on_after": 0.0, "ess_b": 0.0, "ess_a": 0.0})
                    s["z"] += z * share
                    aft = pw * P / z
                    s["on_before"] += float((pw * on_p2).sum()) * share
                    s["on_after"] += float((aft * on_p2).sum()) * share
                    s["ess_b"] += float(1.0 / np.sum(pw ** 2))
                    s["ess_a"] += float(1.0 / np.sum(aft ** 2))
                    h = half_of[sd]
                    hh = half.setdefault(k, [[0.0, 0.0], [0.0, 0.0]])
                    hh[h][0] += z * share
                    hh[h][1] += share
            print(f"  {d.name}/{sd.name} done", flush=True)

    report = {}
    for (key, lab, arm), s in acc.items():
        hh = half[(key, lab, arm)]
        report.setdefault(key, {}).setdefault(arm, {})[lab] = {
            "kind": s["kind"], "evidence_z": s["z"],
            "z_half": [hh[0][0] / hh[0][1] if hh[0][1] else None,
                       hh[1][0] / hh[1][1] if hh[1][1] else None],
            "on_phase2_before": s["on_before"], "on_phase2_after": s["on_after"],
            "ess_before": s["ess_b"], "ess_after": s["ess_a"],
            "estimable": bool(s["ess_a"] >= ESS_FLOOR),
        }
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    for key in sorted(report):
        for arm in sorted(report[key]):
         for lab in [s[0] for s in scen]:
            r = report[key][arm][lab]
            print(f"{key:40s} {arm:24s} {lab:42s} Z {r['evidence_z']:.4f}  "
                  f"on P2 {r['on_phase2_before']:.3f} -> {r['on_phase2_after']:.3f}  "
                  f"ESS {r['ess_after']:12,.0f}  {'' if r['estimable'] else 'NOT ESTIMABLE'}")


if __name__ == "__main__":
    main()
