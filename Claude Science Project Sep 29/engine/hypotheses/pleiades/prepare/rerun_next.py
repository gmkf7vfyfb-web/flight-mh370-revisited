"""Overnight 10-11 Oct (OVERNIGHT-2026-10-10.md, Searched areas / Pleiades / settling): the Pleiades standard
result on end of flight's NEW impacts, across every 00:19 option present, never as one number.

    python rerun_next.py <impacts root> <tag> [labels] [--pfamily s1=p1,s2=p2,...] [--geom <dir>]

<impacts root>/seed-<k>/{impacts.npy,COLUMNS.txt,run.json}  e.g. mh370-exchange/end-of-flight/next-run
<tag>                                                       output name (each option run plain and +alive): runs/pleiades/<tag>/, results/pleiades/<tag>/
[labels]                                                    e.g. "uncorrected fuel; provisional sampler; PROVISIONAL-OVERNIGHT"

Steps (cargo env from the caller: toolchain on PATH, CARGO_TARGET_DIR, RAYON_NUM_THREADS <= 4):
  1. `mh370 evaluate` of the searched-areas module alone, base (Phase 2 + Bluefin-21) and + OI 2018 + 2025-26 SE
     (runs/pleiades/eval-oi/{base,oi2018-2025}.toml), on every seed. The search column is that module's own.
  2. branch_eof289.py per 00:19 option (loglik:<option> columns in COLUMNS.txt) and per search variant, with this
     module's exported surfaces (runs/pleiades/{likelihood,cosmo}-surface).
  3. branch_figure.py per option (base search), footnote built from run.json.
  4. the standard close-ups for every option (closeup_styles.standard: colour and seabed, all four COSMO contacts),
     strata mixed by --pfamily when present
  5. results/pleiades/<tag>/by-0019-option.csv: P, C3, C4, P+C3, P+C4 before/after search per option and variant.
Generated output goes to the gitignored run tree; only the summary, figures and the note go to results/.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
MOD = HERE.parent
ENGINE = MOD.parents[1]
CSP = ENGINE.parent
RUNS = ENGINE / "runs" / "pleiades"
# Surfaces the branch reads: default the module's run tree (85-103 E, 43-25 S); `--surfaces runs/pleiades/wide` for the coverage grid
# (78-115 E, 45-5 S; composer ruling 1), which run C uses.
SURF = RUNS
VARIANTS = {"base": "Phase 2 + Bluefin-21", "oi2018-2025": "+ OI 2018 + OI 2025-26 SE band"}


def sh(cmd, cwd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), cwd=cwd, check=True)


def options(root):
    from compact_eval import seed_dirs, seed_reader
    cols, _, _ = seed_reader(seed_dirs(root)[0])
    return [c.split(":", 1)[1] for c in cols if c.startswith("loglik:")]


def main(root, tag, labels="", only=None):
    root = Path(root).resolve()
    from compact_eval import seed_dirs, eval_input
    seeds = seed_dirs(root)
    assert seeds, f"no seed-* under {root}"
    out = RUNS / tag
    res = CSP / "results" / "pleiades" / tag
    res.mkdir(parents=True, exist_ok=True)
    for v in VARIANTS:
        for s in seeds:
            d = out / f"eval-{v}" / s.name
            if (d / "evaluate.npy").exists():
                continue
            src = eval_input(s, out / "eval-input")  # run C compact: rebuilt 21-column file (compact_eval.py), deleted below
            sh(["cargo", "run", "--offline", "-j", "2", "--release", "-q", "--", "evaluate", "hypotheses/seabed-search/run.toml",
                RUNS / "eval-oi" / f"{v}.toml", src, d], cwd=ENGINE)
            if src != s / "impacts.npy":
                src.unlink()
    # every 00:19 option plain, and under end of flight's provisional reference constraint `+alive` (10 Oct ~04:05 UTC)
    # ruling ~19:10 B: (b) `+unpowered` is the reference existence constraint; `+alive` (a) kept for continuity; `+silent` (c) beside
    opts = [o + c for o in options(root) for c in ("", "+alive", "+unpowered", "+silent")]
    if only:
        opts = list(only)
    rows = []
    for o in opts:
        safe = o.replace("/", "-")
        for v, vlab in VARIANTS.items():
            b = out / f"branch-{safe}-{v}"
            if not (b / "branch.csv").exists():
                sh([sys.executable, HERE / "branch_eof289.py", root, out / f"eval-{v}", SURF, b, o,
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


def main_all(root, tag, labels="", pfamily="", geom=None, only=None, family_evidence=None, surfaces=None):
    global SURF
    if surfaces:
        SURF = Path(surfaces).resolve()
    """Strata-aware entry point. If <impacts root> holds strata (<stratum>/seed-*), run main() per stratum and mix by
    --pfamily (required then); then ALWAYS draw the close-ups for every option (Pete, 10 Oct: close-ups every time)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    import closeup_styles
    gebco = str(Path("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json"))
    root = Path(root).resolve()
    strata = sorted(d.name for d in root.iterdir() if d.is_dir() and (any(d.glob("seed-*/impacts.npy")) or any(d.glob("seed-*/impacts32.npy"))))
    geom = geom or str(CSP.parents[1] / "geom")
    if strata:
        fe0 = family_evidence or next(iter(sorted((root / "summary").glob("family-evidence-*.json"))), None)
        pf = {k: float(v) for k, v in (x.split("=") for x in pfamily.split(",") if x)}
        if not pf and fe0:   # core's fixed P(family), as end of flight records it (`p_core`)
            pf = {k: float(v) for k, v in json.loads(Path(fe0).read_text())["p_core"].items()}
            print("P(family) from", fe0, pf)
        assert set(pf) == set(strata), f"--pfamily must name every stratum {strata}"
        for st in strata:
            main(root / st, f"{tag}/{st}", f"{labels}; stratum {st}" if labels else f"stratum {st}", only)
        opts = json.loads((CSP / "results" / "pleiades" / tag / strata[0] / "provenance.json").read_text())["options"]
        # ruling C: mix by end of flight's 00:19-re-weighted P(family) when it has published it; fixed weights beside
        fe = family_evidence or next(iter(sorted((root / "summary").glob("family-evidence-*.json"))), None)
        if fe is None:
            print("NOTE: no end-of-flight family-evidence file; strata mixed at fixed P(family) only")
        closeup_styles.standard(RUNS / tag, root, geom, gebco, CSP / "results" / "pleiades" / tag / "closeups", plt, pf, opts, labels,
                                fam_json=str(fe) if fe else None, surf=SURF)
    else:
        main(root, tag, labels, only)
        opts = json.loads((CSP / "results" / "pleiades" / tag / "provenance.json").read_text())["options"]
        closeup_styles.standard(RUNS / tag, root, geom, gebco, CSP / "results" / "pleiades" / tag / "closeups", plt, None, opts, labels)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("tag"); ap.add_argument("labels", nargs="?", default="")
    ap.add_argument("--pfamily", default="", help="stratum=P(family),... when the impacts come in strata")
    ap.add_argument("--geom", default=None, help="directory with search_footprints.geojson")
    ap.add_argument("--family-evidence", default=None, help="end of flight's family-evidence-*.json (default: <root>/summary/)")
    ap.add_argument("--surfaces", default=None, help="surface dir for the branch (default runs/pleiades; run C: runs/pleiades/wide)")
    ap.add_argument("--options", default="", help="comma-separated end-of-flight arms to run (default: every loglik column, plain and +alive)")
    a = ap.parse_args()
    main_all(a.root, a.tag, a.labels, a.pfamily, a.geom, [x for x in a.options.split(",") if x] or None, a.family_evidence, a.surfaces)
