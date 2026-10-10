"""Stand-in combiner (not module code): mixes the Pleiades module's per-stratum branch outputs
(prepare/rerun_next.py -> branch_eof289.py at ed85311) over core's (b) strata with P(family) held fixed,
using the module's own summarise() on the module's own headline arm (rho4-0, equal clusters, both ocean models).
It first re-derives each stratum's pooled rows from branch-maps.npz and checks them against branch.csv.

    python combine_mixture.py <runs/pleiades/next-run-b-standin> <results/pleiades/next-run-b-standin>
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

WS = Path(__file__).resolve().parent
PREP = WS / "pl/Claude Science Project Sep 29/engine/hypotheses/pleiades/prepare"
sys.path.insert(0, str(PREP))
import branch_eof289 as B  # noqa: E402

PFAM = {"next-free": 0.6948, "next-repro-radar": 0.1527, "next-descent-climb": 0.1376, "next-routes": 0.0149}
VARIANTS = {"base": "Phase 2 + Bluefin-21", "oi2018-2025": "+ OI 2018 + OI 2025-26 SE band"}
FIELDS = ["P", "C3", "C4", "P+C3", "P+C4"]


def rows_from_maps(pre, post, Z, v):
    lat, lon, area = Z["lat"], Z["lon"], Z["area"]
    dummy = np.zeros_like(area, dtype=bool)
    out = []
    for f in FIELDS:
        L = Z[f"L_{f}"]
        for stage, pc in [("before search", pre), ("after search", post)]:
            if v != "base" and stage == "before search":
                continue
            r = B.summarise(pc, L, area, lat, lon, dummy, dummy, dummy)
            zh = float((pc / pre.sum() * L).sum() / (pre / pre.sum() * L).sum()) if stage == "after search" else 1.0
            out.append(dict(search=VARIANTS[v] if stage == "after search" else "none", field=f, stage=stage,
                            median_lat=round(r["cond_median_lat"], 3), mean_lat=round(r["cond_mean_lat"], 3),
                            mean_lon=round(r["cond_mean_lon"], 3), mean_shift_nm=round(r["mean_shift_nm"], 1),
                            cond_hdr90_km2=round(r["cond_hdr90_km2"]), uncond_hdr90_km2=round(r["uncond_hdr90_km2"]),
                            ln_S=round(r["ln_S"], 3), tension_p=round(r["tension_p"], 3), retained_under_H=round(zh, 3),
                            retained_unconditional=round(float(pc.sum() / pre.sum()), 3)))
    return out


def main(runs, res):
    runs, res = Path(runs), Path(res)
    (res / "mixture").mkdir(parents=True, exist_ok=True)
    opts = json.loads((res / "next-free" / "provenance.json").read_text())["options"]
    rows, checks = [], []
    for o in opts:
        safe = o.replace("/", "-")
        for v in VARIANTS:
            pre = post = None; og = []
            for s, pi in PFAM.items():
                b = runs / s / f"branch-{safe}-{v}"
                Z = np.load(b / "branch-maps.npz")
                # check: the stratum's own pooled headline rows re-derive from its maps
                mine = pd.DataFrame(rows_from_maps(Z["pre"], Z["post"], Z, v))
                t = pd.read_csv(b / "branch.csv")
                t = t[(t.ocean_model == "both models") & (t.replicate == "pooled") &
                      (((t.object_rating == "rho4-0") & (t.cluster_weight == "equal")) | (t.object_rating.isna() & ~t.field.str.contains("P")))]
                for _, m in mine.iterrows():
                    q = t[(t.field == m.field) & (t.stage == m.stage)].iloc[0]
                    checks.append(dict(stratum=s, option=o, variant=v, field=m.field, stage=m.stage,
                                       d_median=abs(m.median_lat - round(q.cond_median_lat, 3)), d_hdr=abs(m.cond_hdr90_km2 - round(q.cond_hdr90_km2)),
                                       d_lnS=abs(m.ln_S - round(q.ln_S, 3)), d_ret=abs(m.retained_under_H - round(q.search_retained_under_H, 3))))
                for r in mine.to_dict("records"):
                    rows.append(dict(stratum=s, option=o, **r))
                pre = pi * Z["pre"] if pre is None else pre + pi * Z["pre"]
                post = pi * Z["post"] if post is None else post + pi * Z["post"]
                og += json.loads((b / "branch.json").read_text())["uncond_mass_outside_grid"]
                Zk = Z
            for r in rows_from_maps(pre, post, Zk, v):
                rows.append(dict(stratum="mixture", option=o, **r))
            if v == "base":
                d = runs / "mixture" / f"branch-{safe}-{v}"
                d.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(d / "branch-maps.npz", lat=Zk["lat"], lon=Zk["lon"], area=Zk["area"], pre=pre, post=post,
                                    **{f"L_{f}": Zk[f"L_{f}"] for f in FIELDS})
                (d / "branch.json").write_text(json.dumps(dict(option=o, label=f"next-run (core (b), 4 strata mixed by P(family)); 00:19 option {o}; search {VARIANTS[v]}",
                                                               uncond_mass_outside_grid=og, pfam=PFAM), indent=1))
    S = pd.DataFrame(rows)
    S.to_csv(res / "mixture" / "by-0019-option-by-stratum-and-mixture.csv", index=False)
    C = pd.DataFrame(checks)
    C.to_csv(res / "mixture" / "check-maps-vs-branch-csv.csv", index=False)
    print("max check diffs", C[["d_median", "d_hdr", "d_lnS", "d_ret"]].max().to_dict())


if __name__ == "__main__":
    main(*sys.argv[1:3])
