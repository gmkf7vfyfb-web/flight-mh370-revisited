"""Stand-in (architecture, for hydroacoustics, 11 Oct 2026): run C detectability sensitivity with end of flight's tau sidecars.

Replays the module's OWN per-impact writer (prepare/per_impact_lnl.py, amendment 2 daa7abc3, bug fix 3b5b4446, the
commit recorded in mh370-exchange/hydroacoustics/next-run-c/MODULE_COMMIT) with ONE input changed: the nuisance tau
(log-uniform 0.05-10 s scenario prior, lhyd.Model.nuisance) is replaced row by row with end of flight's
energy_transfer_tau90_s from next-run-c/<stratum>/seed-k/tau90_v1.npz (impact_tau_method = 1, ruling 8dbefed2 item 2;
method note results/eof-impact-tau-method-oct11.md). The nuisance stream is drawn exactly as before and only tau is
overwritten, so z_s, calibration error, C_rcv and C_ims are the same per row: the comparison is paired.
Defaults as the module's run C (--calerr structured, --noise blackman). Interpretation (declared): the mechanical
energy-transfer duration is used AS the acoustic source duration; the module owns that mapping and has not ruled on it.
Tau outside the module grid [0.05, 10] s is clamped by the module's own np.interp lookups (counted, reported).

Output: <out>/<stratum>/seed-k/lnL_soft_tau90.npy (float32, row-aligned) and <out>/summary.json.
--check-baseline recomputes the scenario-tau column first and compares it with the module's run C column.
"""
import argparse, json, pathlib, sys, time
import numpy as np

ap = argparse.ArgumentParser()
for a in ("prepare_dir", "module_dir", "eof_run", "hydro_run", "out", "kadri_csv", "compact_reader"):
    ap.add_argument(a)
ap.add_argument("--strata", nargs="+", default=["next-c-free", "next-c-repro-radar", "next-c-descent-climb", "next-c-routes"])
ap.add_argument("--seeds", nargs="+", type=int, default=list(range(1, 9)))
ap.add_argument("--check-baseline", action="store_true")
ap.add_argument("--no-columns", action="store_true")
a = ap.parse_args()
sys.path.insert(0, a.prepare_dir); sys.path.insert(0, a.prepare_dir + "/exploratory/pleiades_test")
import importlib.util
import per_impact_lnl as PL  # noqa: E402
spec = importlib.util.spec_from_file_location("compact_impacts", a.compact_reader); compact = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(pathlib.Path(a.compact_reader).parent)); spec.loader.exec_module(compact)


class TermsTau(PL.Terms):
    tau_override = None

    def nuisance(self, rng, n):
        nu = PL.Terms.nuisance(self, rng, n)
        if self.tau_override is not None:
            assert len(self.tau_override) == n, (len(self.tau_override), n)
            nu["tau"] = np.asarray(self.tau_override, float).copy()
        return nu


def stats(x):
    return dict(q01=float(np.quantile(x, 0.01)), q50=float(np.quantile(x, 0.5)), q99=float(np.quantile(x, 0.99)),
                share_le_m1=float(np.mean(x <= -1.0)), share_ge_p1=float(np.mean(x >= 1.0)), mean=float(np.mean(x)))


m = TermsTau(a.module_dir, str(pathlib.Path(a.prepare_dir) / "exploratory/pleiades_test/imos_events_searched.json"), a.kadri_csv)
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
sf = out / "summary.json"
summ = json.loads(sf.read_text()) if sf.exists() else {}
summ["options"] = dict(calerr=PL.Terms.calerr, noise=PL.Terms.noise, tau="end-of-flight tau90_v1 (impact_tau_method=1)")
for stratum in a.strata:
    si = PL.stratum_index(stratum)
    for k in a.seeds:
        sd = pathlib.Path(a.eof_run) / stratum / f"seed-{k}"
        if not sd.is_dir():
            continue
        t0 = time.time(); D = PL.load(sd, compact); n = len(D["unix_s"])
        ok = np.isfinite(D["unix_s"]) & np.isfinite(D["latitude_deg"]) & np.isfinite(D["longitude_deg"]) & np.isfinite(D["kinetic_energy_j"])
        z = np.load(sd / "tau90_v1.npz"); assert int(z["method"]) == 1; tau = z["tau90_s"].astype(float); assert len(tau) == n
        base = np.load(pathlib.Path(a.hydro_run) / stratum / f"seed-{k}" / "hydro-lnL.npy", mmap_mode="r")["lnL_soft"]
        base = np.asarray(base, float); assert len(base) == n
        rec = {}
        if a.check_baseline:
            m.tau_override = None
            im, hh = m.soft(D["unix_s"][ok], D["latitude_deg"][ok], D["longitude_deg"][ok], D["kinetic_energy_j"][ok], [20261010, si, k])
            rec["baseline_reproduction_max_abs_diff"] = float(np.max(np.abs((im + hh) - base[ok])))
        m.tau_override = tau[ok]
        im, hh = m.soft(D["unix_s"][ok], D["latitude_deg"][ok], D["longitude_deg"][ok], D["kinetic_energy_j"][ok], [20261010, si, k])
        new = np.full(n, np.nan); new[ok] = im + hh
        tk = tau[ok]
        rec.update(rows=int(n), not_computed=int((~ok).sum()), seconds=round(time.time() - t0, 1),
                   tau90=dict(q05=float(np.quantile(tk, .05)), q50=float(np.quantile(tk, .5)), q95=float(np.quantile(tk, .95)),
                              share_below_0p05=float(np.mean(tk < 0.05)), share_above_10=float(np.mean(tk > 10.0)), nan=int(np.isnan(tk).sum())),
                   scenario_tau=stats(base[ok]), eof_tau90=stats(new[ok]), paired_diff=stats(new[ok] - base[ok]),
                   eof_tau90_imos=stats(im), eof_tau90_h01w=stats(hh))
        summ[f"{stratum}/seed-{k}"] = rec
        if not a.no_columns:
            od = out / stratum / f"seed-{k}"; od.mkdir(parents=True, exist_ok=True); np.save(od / "lnL_soft_tau90.npy", new.astype(np.float32))
        sf.write_text(json.dumps(summ, indent=1))
        print(f"{stratum}/seed-{k}: {n} rows {rec['seconds']} s", rec.get("baseline_reproduction_max_abs_diff", ""), flush=True)
