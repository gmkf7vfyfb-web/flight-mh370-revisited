"""Export the composer's per-row mixture weights for settling's aimed resample (composer gap G12; settling 10-11 Oct 2026).

Run inside the composer's per-stratum loop, AFTER summarise_stratum.py and BEFORE `rm -rf .../weights` (run_pass0.sh line 22):

    "$PY" <settling results>/export_row_weights.py "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST" <out root> <stratum-weights.json> [<tag-pid> ...]

<stratum-weights.json>: {"<tag>": {"<stratum>": W_Q, ...}, ...}: the stratum weight of each composed mixture (the composer's primary
is end of flight's 00:19-re-weighted P(family); seabed_extract.py uses the same). Products default to heldout-/r600- x G, Ga, H, Ha.

Writes <out root>/<tag>-<pid>/<stratum>/seed-<k>.f32 = W_Q(stratum) x w(row) x pooled factor(seed, mode) / (stratum sum of
w x factor), i.e. the row's final mixture mass (the raw sum is kept in pooled_raw_sum.json), one f32 per impacts.npy row in row order (the composer's inputs are row-aligned with impacts.npy; checked through
the parent column). After the last stratum, call with --finish to write manifest.json, SHA256SUMS and READY for each product.
This uses the composer's own pooling (summarise_stratum.pooling) and reads nothing it does not already read; it changes nothing.
"""
import hashlib, json, pathlib, sys
import numpy as np

DEFAULT = [f"{t}-{p}" for t in ("heldout", "r600") for p in ("G", "Ga", "H", "Ha")]
LABEL = {"heldout": ("00:19 Held Out", "none__other"), "r600": ("00:19 R600 BTO Only", "r600-bto__other")}
PNAME = {"G": "G (general)", "Ga": "G after the searches", "H": "H (Pléiades)", "Ha": "H after the searches"}


def export(stratum, ind, rout, outroot, wq_json, *products):
    comp = pathlib.Path(__file__).resolve().parents[1] / "composer-pass0"; sys.path.insert(0, str(comp))
    import summarise_stratum as S
    ind, rout, outroot = pathlib.Path(ind), pathlib.Path(rout), pathlib.Path(outroot)
    WQ = json.loads(pathlib.Path(wq_json).read_text())
    prods = {p["id"]: p for p in json.loads((rout / "products.json").read_text())["products"]}
    for tp in (products or DEFAULT):
        tag = tp.split("-")[0]; fac = S.pooling([r["modes"] for r in prods[tp]["replicates"]])[0]
        od = outroot / tp / stratum; od.mkdir(parents=True, exist_ok=True)
        pooled = {}
        for k in range(1, len(fac) + 1):
            f = rout / "weights" / tp / f"seed-{k}.f32"
            if not f.exists(): continue
            d, h = S.load_inputs(ind, k, ["mode"]); wq = np.fromfile(f, dtype="<f4").astype(np.float64)
            assert wq.size == d["mode"].size, f"{tp} seed {k}: weights {wq.size} vs inputs {d['mode'].size}"
            pooled[k] = wq * fac[k - 1][d["mode"].astype(int)]
        raw = sum(float(np.nansum(v)) for v in pooled.values()); assert raw > 0, f"{tp} {stratum}: zero pooled mass"
        for k, v in pooled.items():
            (WQ[tag][stratum] * v / raw).astype("<f4").tofile(od / f"seed-{k}.f32")   # stratum mass = W_Q exactly
        (od / "pooled_raw_sum.json").write_text(json.dumps({"raw_pooled_sum": raw, "W_Q": WQ[tag][stratum], "seeds": sorted(pooled)}))
        print(tp, stratum, "seeds", sorted(pooled), "raw pooled sum", raw, flush=True)

def finish(outroot, run_root, constraint, *products):
    outroot = pathlib.Path(outroot)
    for tp in (products or DEFAULT):
        d = outroot / tp; tag, pid = tp.split("-", 1); lab, opt = LABEL[tag]
        strata = sorted(p.name for p in d.iterdir() if p.is_dir()); seeds = sorted({int(f.stem.split("-")[1]) for s in strata for f in (d / s).glob("seed-*.f32")})
        (d / "manifest.json").write_text(json.dumps({"product": tp, "label": f"{lab}, {PNAME.get(pid, pid)}", "option": opt, "constraint": constraint,
                                                    "run_root": run_root, "strata": strata, "seeds": seeds}, indent=1))
        lines = [f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(d)}" for f in sorted(d.rglob("*")) if f.is_file() and f.name not in ("SHA256SUMS", "READY")]
        (d / "SHA256SUMS").write_text("\n".join(lines) + "\n"); (d / "READY").write_text("ready\n"); print(tp, len(lines), "files")


if __name__ == "__main__":
    if sys.argv[1] == "--finish": finish(*sys.argv[2:])
    else: export(*sys.argv[1:])
