"""R_hyd on end of flight's full impact rows (pre-registration sections 1, 4, 7). Stand-in, not module code.

Per stratum and seed: reads the needed impact columns ONCE in row chunks (memmap, column subset), serves them to
end of flight's option_posteriors UNCHANGED (its module-level `np` is replaced by a proxy whose load() returns the
in-memory column store; every other numpy call passes through), joins the Pleiades columns (row-aligned; `row` and
`parent` checked), computes L_hyd with lhyd.Model.station_terms, and writes per-seed log sums. The mixture, split-half
and both stratum weightings are formed afterwards by rhyd_mix().

Usage: python rhyd_result.py <module_dir> <imos_events.json> <kadri.csv> <eof_displacement_hist.py> <eof_next_run> <pleiades_next_run_b> <out_dir>
"""
import importlib.util, json, pathlib, sys, time
import numpy as np
from scipy.special import logsumexp
import lhyd

STRATA = ["next-free", "next-repro-radar", "next-descent-climb", "next-routes"]   # core order (rng stream index)
OPTS = {"00:19 R600 BTO Only": "r600-bto__other+alive", "00:19 Held Out": "none__other+alive",
        "00:19 R600 BTO + Raw BFO": "r600_no-offset__other+alive"}
BASE = {"r600-bto__other+alive": "r600-bto", "none__other+alive": "none", "r600_no-offset__other+alive": "r600/no-offset"}
CHUNK = 200_000


class Store:
    def __init__(self, data, cols):
        self.d, self.idx = data, {i: n for n, i in cols.items()}
    def __getitem__(self, key):
        return self.d[self.idx[key[1]]]


class NPProxy:
    def __init__(self, store):
        self.store = store
    def load(self, *a, **k):
        return self.store
    def __getattr__(self, k):
        return getattr(np, k)


def needed(meta):
    c = meta["impact_columns"]
    want = ["weight", "parent", "family", "unix_s", "latitude_deg", "longitude_deg", "kinetic_energy_j", "vertical_kinetic_energy_j",
            "latent:last_burst_latitude_deg", "latent:last_burst_longitude_deg", "latent:realised_flameout_unix_s",
            "latent:spiral_divergent", "bto_residual_us:m0019a", "bto_residual_us:m0019b"] + [x for x in c if x.startswith("loglik:")]
    return [x for x in want if x in c]


def read_cols(path, meta, names):
    X = np.load(path, mmap_mode="r"); cols = {n: i for i, n in enumerate(meta["impact_columns"])}; ix = [cols[n] for n in names]
    out = np.empty((len(names), X.shape[0]))
    for s in range(0, X.shape[0], CHUNK):
        out[:, s:s + CHUNK] = np.asarray(X[s:s + CHUNK])[:, ix].T
    return {n: out[k] for k, n in enumerate(names)}


def lse_w(lp, lx, m):
    return float(logsumexp(lp[m] + lx[m])) if m.any() else -np.inf


def main():
    mod, evj, kd, eofp, eofrun, plrun, outd = sys.argv[1:8]
    out = pathlib.Path(outd); out.mkdir(parents=True, exist_ok=True)
    m = lhyd.Model(mod, evj, kd)
    spec = importlib.util.spec_from_file_location("eof_dh", eofp); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
    dh.SATCOM_CSV = pathlib.Path(eofp).resolve().parents[3] / "data" / "satcom-observations.csv"
    rows = []
    for si, stratum in enumerate(STRATA):
        for sd in sorted((pathlib.Path(eofrun) / stratum).glob("seed-*")):
            t0 = time.time(); k = int(sd.name.split("-")[1])
            meta = json.loads((sd / "run.json").read_text()); names = needed(meta)
            data = read_cols(sd / "impacts.npy", meta, names); n = len(data["weight"])
            store = Store(data, {nm: meta["impact_columns"].index(nm) for nm in names})
            dh.np = NPProxy(store)
            g = lambda nm: data[nm]
            logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
            present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
            derived = dh.derived_logliks(meta, g, present)
            Pl = np.load(pathlib.Path(plrun) / stratum / sd.name / "pleiades-lnL.npy", mmap_mode="r")
            assert len(Pl) == n and np.array_equal(np.asarray(Pl["row"]), np.arange(n)), "Pleiades rows not aligned"
            assert np.array_equal(np.asarray(Pl["parent"]), data["parent"] if "parent" in data else np.asarray(Pl["parent"]))
            lnLP = np.asarray(Pl["lnL_both_mean"], float); nc = np.asarray(Pl["not_computed"]).astype(bool)
            assert np.all(np.isfinite(lnLP[~nc])), "non-finite lnL on computed rows"
            rng_seed = [20261010, si, k]
            th = m.station_terms(data["unix_s"], data["latitude_deg"], data["longitude_deg"], data["kinetic_energy_j"], np.random.default_rng(rng_seed), "A")
            tv = m.station_terms(data["unix_s"], data["latitude_deg"], data["longitude_deg"], data["vertical_kinetic_energy_j"], np.random.default_rng(rng_seed), "A")
            L = {"A": th["total"], "A-IMOS": sum(th[lg] for lg in m.B.LOGGERS), "A-VKE": tv["total"], "H01W-only": th["H01W"]}
            got = {}
            for key, p, _c in dh.option_posteriors(sd, sd, constraints=("alive",)):
                if key in BASE:
                    got[key] = p
            w = data["weight"]
            for name, key in OPTS.items():
                p = got[key]; lp = np.log(np.where(p > 0, p, np.nan)); lp = np.where(np.isfinite(lp), lp, -np.inf)
                b = BASE[key]; base = derived[b] if b in derived else data["loglik:" + b]
                ll = np.where(np.isfinite(base), base, -np.inf) + dh.constraint_log_factor(g, logon, "other", "alive")
                with np.errstate(divide="ignore"):
                    lz = float(logsumexp(np.log(w) + ll) - np.log(w.sum()))
                    pq = w * np.exp(ll - ll[np.isfinite(ll)].max()); pq /= pq.sum()
                chk = float(np.max(np.abs(pq - p)))
                comp = ~nc & np.isfinite(lp); allr = np.isfinite(lp)
                lpH = lp + np.where(nc, -np.inf, lnLP)
                r = dict(stratum=stratum, si=si, seed=k, option=name, key=key, n_rows=n, ln_Z0019=lz, check_p_maxabs=chk,
                         not_computed_rows=int(nc.sum()), not_computed_weight=float(p[nc].sum()),
                         ess_flight=float(1 / np.sum(p ** 2)), ess_H=float(np.exp(2 * logsumexp(lpH) - logsumexp(2 * lpH))),
                         lnS0=lse_w(lp, np.zeros(n), allr), lnS0_comp=lse_w(lp, np.zeros(n), comp), lnSH=lse_w(lp, lnLP, comp))
                for v, lh in L.items():
                    r[f"lnS0L|{v}"] = lse_w(lp, lh, allr); r[f"lnS0L_comp|{v}"] = lse_w(lp, lh, comp); r[f"lnSHL|{v}"] = lse_w(lp, lnLP + lh, comp)
                rows.append(r)
            print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s, check {max(r['check_p_maxabs'] for r in rows[-3:]):.2e}", flush=True)
            del data, store, th, tv, L, got
            (out / "per_seed.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
