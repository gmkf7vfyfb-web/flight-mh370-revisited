"""Overnight 10-11 Oct (OVERNIGHT-2026-10-10.md, Searched areas / Pleiades / settling): the Pleiades standard
result on end of flight's NEW impacts, across every 00:19 option present, never as one number.

    python rerun_next.py <impacts root> <tag> [labels]

<impacts root>/seed-<k>/{impacts.npy,COLUMNS.txt,run.json}  e.g. mh370-exchange/end-of-flight/next-run
<tag>                                                       output name (each option run plain and +alive): runs/pleiades/<tag>/, results/pleiades/<tag>/
[labels]                                                    e.g. "uncorrected fuel; provisional sampler; PROVISIONAL-OVERNIGHT"

Steps (cargo env from the caller: toolchain on PATH, CARGO_TARGET_DIR, RAYON_NUM_THREADS <= 4):
  1. `mh370 evaluate` of the searched-areas module alone, base (Phase 2 + Bluefin-21) and + OI 2018 + 2025-26 SE
     (runs/pleiades/eval-oi/{base,oi2018-2025}.toml), on every seed. The search column is that module's own.
  2. branch_eof289.py per 00:19 option (loglik:<option> columns in COLUMNS.txt) and per search variant, with this
     module's exported surfaces (runs/pleiades/{likelihood,cosmo}-surface).
  3. branch_figure.py per option (base search), footnote built from run.json.
  4. results/pleiades/<tag>/by-0019-option.csv: P, C3, C4, P+C3, P+C4 before/after search per option and variant.
Generated output goes to the gitignored run tree; only the summary, figures and the note go to results/.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
ENGINE = MOD.parents[1]
CSP = ENGINE.parent
RUNS = ENGINE / "runs" / "pleiades"
VARIANTS = {"base": "Phase 2 + Bluefin-21", "oi2018-2025": "+ OI 2018 + OI 2025-26 SE band"}


def sh(cmd, cwd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), cwd=cwd, check=True)


def options(root):
    cols = (sorted(Path(root).glob("seed-*"))[0] / "COLUMNS.txt").read_text().split()
    return [c.split(":", 1)[1] for c in cols if c.startswith("loglik:")]


def main(root, tag, labels=""):
    root = Path(root).resolve()
    seeds = sorted(root.glob("seed-*"))
    assert seeds, f"no seed-* under {root}"
    out = RUNS / tag
    res = CSP / "results" / "pleiades" / tag
    res.mkdir(parents=True, exist_ok=True)
    for v in VARIANTS:
        for s in seeds:
            d = out / f"eval-{v}" / s.name
            if (d / "evaluate.npy").exists():
                continue
            sh(["cargo", "run", "--offline", "-j", "2", "--release", "-q", "--", "evaluate", "hypotheses/seabed-search/run.toml",
                RUNS / "eval-oi" / f"{v}.toml", s / "impacts.npy", d], cwd=ENGINE)
    # every 00:19 option plain, and under end of flight's provisional reference constraint `+alive` (10 Oct ~04:05 UTC)
    opts = [o + c for o in options(root) for c in ("", "+alive")]
    rows = []
    for o in opts:
        safe = o.replace("/", "-")
        for v, vlab in VARIANTS.items():
            b = out / f"branch-{safe}-{v}"
            if not (b / "branch.csv").exists():
                sh([sys.executable, HERE / "branch_eof289.py", root, out / f"eval-{v}", RUNS, b, o,
                    f"{root.name}; 00:19 option {o}; search {vlab}" + (f"; {labels}" if labels else "")], cwd=HERE)
            t = pd.read_csv(b / "branch.csv")
            t = t[(t.ocean_model == "both models") & (t.object_rating == "rho4-0") & (t.cluster_weight == "equal") & (t.replicate == "pooled")]
            for _, r in t.iterrows():
                if v != "base" and r.stage == "before search":
                    continue
                rows.append(dict(option=o, search=vlab if r.stage == "after search" else "none", field=r.field, stage=r.stage,
                                 median_lat=round(r.cond_median_lat, 3), mean_lat=round(r.cond_mean_lat, 3), mean_lon=round(r.cond_mean_lon, 3),
                                 mean_shift_nm=round(r.mean_shift_nm, 1), cond_hdr90_km2=round(r.cond_hdr90_km2),
                                 uncond_hdr90_km2=round(r.uncond_hdr90_km2), ln_S=round(r.ln_S, 3), tension_p=round(r.tension_p, 3),
                                 retained_under_H=round(r.search_retained_under_H, 3), retained_unconditional=round(r.search_retained_unconditional, 3)))
            if v == "base":
                sh([sys.executable, HERE / "branch_figure.py", b, MOD, res / f"branch-{safe}", labels], cwd=HERE)
    S = pd.DataFrame(rows)
    S.to_csv(res / "by-0019-option.csv", index=False)
    info = json.loads((out / f"branch-{opts[0].replace('/', '-')}-base" / "branch.json").read_text())
    (res / "provenance.json").write_text(json.dumps(dict(impacts_root=str(root), options=opts, seeds=[s.name for s in seeds],
                                                         labels=labels, variants=VARIANTS, models=info["models"]), indent=1))
    print(S[(S.field.isin(["P+C3", "P+C4"]))].to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
