"""Composer pass 1 (seabed step): for settling's own core-set resample on core (b), find each resampled impact's
end-of-flight row and record, at that row, the composed pooled weight of every product and the density the
resample was drawn from.

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.

Settling's run (results/settling-core-set-next-run-b/, hypothesis/settling 5b595bf, wf_standard.py): per option j, stratum
and seed, a systematic resample of end of flight's option posterior under `unpowered` (displacement_hist.py at 43262c31,
sha256 d8149214... = the repo HEAD copy used here), then a stride sub-sample per mixture (`reweighted_j` mask). Options used
here: j = 0 00:19 Held Out (none__other, table A), j = 1 00:19 R600 BTO Only (r600-bto__other, table B). Tables carry
VCOLS (unix_s, lat, lon, ..., parent at 10) + draws + si*10+seed.

Matching, as the Pleiades-conditional stand-in did: (stratum, seed, parent, latitude) -> impacts row, exact.

Writes <out>/<stratum>.npz: for j in (0, 1): outcome index, seed, matched row, p_src (the seed-normalised `unpowered`
option posterior at the row), mode, and for each product the composed weight (f32 as written by the composer) and the
pooled factor for the row's (seed, mode), so the pooled within-stratum weight is w x factor.

Usage: python seabed_extract.py <stratum> <input dir> <rust out dir> <out dir>
"""
import importlib.util, json, pathlib, sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import summarise_stratum as S

FIELD = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/770a0941-603a-4490-929c-9fdb91cd5434/field")
REPO = pathlib.Path(__file__).resolve().parents[2]
DH = REPO / "engine/hypotheses/end-of-flight/smoke/displacement_hist.py"
DH_SHA = "d81492148a44b490"
EOF_RUN = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run")
OPTS = {0: ("A", "heldout", "none"), 1: ("B", "r600", "r600-bto")}
PRODUCTS = ["P1", "G", "Ga", "H", "Ha", "Gx", "Hx"]


def main(stratum, ind, rout, outd):
    import hashlib
    assert hashlib.sha256(DH.read_bytes()).hexdigest().startswith(DH_SHA), "displacement_hist.py changed"
    spec = importlib.util.spec_from_file_location("dh", DH); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
    dh.SATCOM_CSV = REPO / "engine/data/satcom-observations.csv"
    ind, rout, outd = pathlib.Path(ind), pathlib.Path(rout), pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    info = json.loads((FIELD / "nrb_info.json").read_text()); si = info["strata"].index(stratum)
    assert info["constraint"] == "unpowered"
    z = np.load(FIELD / "nrb_draws.npz")
    T = {t: np.fromfile(FIELD / f"nrb{t}_impacts.f64", "<f8").reshape(-1, 14) for t in "AB"}
    prods = {p["id"]: p for p in json.loads((rout / "products.json").read_text())["products"]}
    out, check = {}, {}
    for j, (t, tag, opt) in OPTS.items():
        sel = np.where(z[f"stratum_{j}"] == si)[0]
        rec = {"outcome": sel, "seed": z[f"seed_{j}"][sel], "row": np.full(sel.size, -1), "p_src": np.zeros(sel.size), "mode": np.zeros(sel.size, np.int8)}
        fac = {pid: S.pooling([r["modes"] for r in prods[f"{tag}-{pid}"]["replicates"]])[0] for pid in PRODUCTS}
        for pid in PRODUCTS:
            rec[f"w_{pid}"] = np.zeros(sel.size, np.float32); rec[f"f_{pid}"] = np.zeros(sel.size)
        for k in (1, 2, 3, 4):
            m = rec["seed"] == k
            if not m.any():
                continue
            tr = T[t][z[f"rows_{j}"][sel[m]]]
            assert np.all(tr[:, 13] == si * 10 + k), "table stratum/seed code"
            d, h = S.load_inputs(ind, k, ["parent", "latitude_deg", "weight", "mode"])
            left = pd.DataFrame({"parent": tr[:, 10], "lat": tr[:, 1], "i": np.arange(m.sum())})
            right = pd.DataFrame({"parent": d["parent"], "lat": d["latitude_deg"], "row": np.arange(d["parent"].size)})
            mm = left.merge(right, on=["parent", "lat"], how="left").drop_duplicates("i").sort_values("i")
            rows = mm["row"].to_numpy(); ok = np.isfinite(rows); rows = np.where(ok, rows, 0).astype(np.int64)
            idx = np.where(m)[0]
            rec["row"][idx] = np.where(ok, rows, -1); rec["mode"][idx] = d["mode"][rows].astype(np.int8)
            # source density: settling's option posterior under `unpowered`, normalised per seed
            sd = EOF_RUN / stratum / f"seed-{k}"; meta = json.loads((sd / "run.json").read_text())
            cols = {c: i for i, c in enumerate(meta["impact_columns"])}
            need = ["unix_s", "latent:realised_flameout_unix_s", "bto_residual_us:m0019a", "bto_residual_us:m0019b"]
            X = np.load(sd / "impacts.npy", mmap_mode="r"); V = {c: np.empty(X.shape[0]) for c in need}
            for s0 in range(0, X.shape[0], 200_000):
                blk = np.asarray(X[s0:s0 + 200_000]); [V[c].__setitem__(slice(s0, s0 + blk.shape[0]), blk[:, cols[c]]) for c in need]
            g = lambda c: V[c]
            present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
            ll = dh.derived_logliks(meta, g, present)["r600-bto"] if opt == "r600-bto" else np.zeros(X.shape[0])
            ll = np.where(np.isfinite(ll), ll, -np.inf) + dh.constraint_log_factor(g, meta["config"]["hypotheses"]["end-of-flight"]["logon"], "other", "unpowered")
            lw = np.log(d["weight"]) + ll; p = np.exp(lw - lw[np.isfinite(lw)].max()); p /= p.sum()
            rec["p_src"][idx] = p[rows]
            check[f"{tag} seed {k}"] = {"ess_src_rows": float(1 / np.sum(p ** 2)), "settling_ess": info["options"]["00:19 Held Out" if j == 0 else "00:19 R600 BTO Only"]["ess_per_stratum_seed"][stratum][str(k)],
                                        "outcomes": int(m.sum()), "matched": int(ok.sum())}
            for pid in PRODUCTS:
                wq = np.fromfile(rout / "weights" / f"{tag}-{pid}" / f"seed-{k}.f32", dtype="<f4")
                rec[f"w_{pid}"][idx] = wq[rows]; rec[f"f_{pid}"][idx] = fac[pid][k - 1][d["mode"][rows].astype(int)]
                pooled = wq.astype(float) * fac[pid][k - 1][d["mode"].astype(int)]
                check[f"{tag} seed {k}"][f"pooled_mass_where_unpowered_is_zero[{pid}]"] = float(pooled[p == 0].sum())
                check[f"{tag} seed {k}"][f"pooled_mass[{pid}]"] = float(pooled.sum())
            del V, X
        for key, v in rec.items():
            out[f"{j}|{key}"] = v
    np.savez_compressed(outd / f"{stratum}.npz", **out)
    (outd / f"{stratum}-check.json").write_text(json.dumps(check, indent=1))
    print(stratum, {k: (v["matched"], v["outcomes"], round(v["ess_src_rows"]), round(v["settling_ess"])) for k, v in check.items()}, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
