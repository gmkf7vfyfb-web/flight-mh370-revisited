"""Per-impact hydroacoustic log-likelihood columns for the composer (end-to-end pass; architecture ruling 15:20 -0600).

Writes, for every end-of-flight impact row, the module's columns in the shared per-impact format, row-aligned with
end of flight's impacts (full `impacts.npy` or compact `impacts32.npy`):
  <out>/<stratum>/seed-<k>/hydro-lnL.npy   structured array:
    row, parent                          end of flight's row index and parent
    lnL_gated                            THE MODULE'S LIKELIHOOD: 0.0 for every row. The P_D gate (brief, contract) admits
                                         no term until raw IMS triad data are held; IMOS non-detection carries < 1e-3 bit.
    lnL_soft                             EXPLORATORY near-limit soft likelihood (declared sensitivity, "hydroacoustics
                                         low-power"): IMOS 3315/3376/3274/3275 scored segments + Kadri Table 1 at H01W
                                         with coverage = Table 1's time-bearing box (module amendment b91b4ed to the
                                         stand-in's lhyd.py, prereg c8b64a8), with P_D <= 201/202 (amendment 1 of
                                         review_rerun.py: the injected range supports no higher P_D).
    lnL_soft_imos, lnL_soft_h01w         its two parts
    not_computed                         1 where the impact row has no finite time or position (excluded, counted)
  plus COLUMNS.txt, SHA256SUMS per seed; README.txt and READY at the top, READY written last.
OBSERVATION IDS (declared): hyd.imos.3315, hyd.imos.3376, hyd.imos.3274, hyd.imos.3275 (scored segments of 8 Mar 2014,
  no events except two loose ones at 3275); hyd.h01w.kadri2024_table1 (19 transients with bearings). None is a raw IMS
  triad record.
NUISANCE: one draw per row (tau, z_s, C_site, C_rcv, C_ims), rng = default_rng([20261010, stratum_index, seed]),
  stratum index in core's order; shared by all stations, as the stand-in.
COMPOSER USE: lnL_gated is the module's contribution. lnL_soft may be composed only as a labelled sensitivity.

Usage (from prepare/, PYTHONPATH=.:exploratory/pleiades_test):
  python per_impact_lnl.py <module_dir> <eof_run_dir> <out_dir> <kadri_table1.csv> [--compact-reader <compact_impacts.py>]
"""
import argparse, hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "exploratory" / "pleiades_test"))
import lhyd                    # noqa: E402  stand-in, unchanged
import review_rerun as RV      # noqa: E402  module amendment (H01W box)

STRATA = ["next-free", "next-repro-radar", "next-descent-climb", "next-routes"]
DT = np.dtype([("row", "<i8"), ("parent", "<i8"), ("lnL_gated", "<f8"), ("lnL_soft", "<f8"), ("lnL_soft_imos", "<f8"),
               ("lnL_soft_h01w", "<f8"), ("not_computed", "u1")])


class Terms(RV.ReviewModel):
    def soft(self, t_unix, lat, lon, E, seed):
        self.cap = RV.PD_CAP
        rng = np.random.default_rng(seed)
        base = self.station_terms(t_unix, lat, lon, E, rng, "A")
        n = len(lat); nu = self.nuisance(np.random.default_rng(seed), n); t0 = t_unix - lhyd.DAY0_UNIX
        snr = self._snr0(lat, E, nu, self.tl_ims["H01W"], "3376") + nu["c_site"] + nu["c_ims"] + lhyd.TRIAD_GAIN_DB
        baz, d = self.geometry(lat, lon, "H01W"); t_arr = t0 + d / lhyd.C_MEAN
        sd_t = np.sqrt(lhyd.PICK_S ** 2 + (d * lhyd.C_SD / lhyd.C_MEAN ** 2) ** 2)
        box = (t_arr >= RV.BOX_T[0]) & (t_arr <= RV.BOX_T[1]) & (baz >= RV.BOX_B[0]) & (baz <= RV.BOX_B[1])
        h = np.log(self._mix(box * self._pd(snr, "3274"), t_arr, sd_t, self.kadri[:, 0], lhyd.KADRI_LAMBDA, baz, self.kadri[:, 1]))
        imos = sum(base[lg] for lg in self.B.LOGGERS)
        return imos, h


def load(sd, compact):
    if (sd / "impacts32.npy").exists():
        meta, g = compact.load(sd)
        get = lambda k: np.asarray(g(k), float)
    else:
        meta = json.loads((sd / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
        X = np.load(sd / "impacts.npy", mmap_mode="r"); get = lambda k: np.asarray(X[:, cols[k]], float)
    return {k: get(k) for k in ("unix_s", "latitude_deg", "longitude_deg", "kinetic_energy_j", "parent")}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("module_dir"); ap.add_argument("eof_run"); ap.add_argument("out"); ap.add_argument("kadri_csv")
    ap.add_argument("--compact-reader"); ap.add_argument("--imos-events", default=str(HERE / "exploratory/pleiades_test/imos_events_searched.json"))
    ap.add_argument("--strata", nargs="+", default=STRATA)
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    compact = None
    if a.compact_reader:
        spec = importlib.util.spec_from_file_location("compact_impacts", a.compact_reader); compact = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(pathlib.Path(a.compact_reader).parent)); spec.loader.exec_module(compact)
    m = Terms(a.module_dir, a.imos_events, a.kadri_csv); summ = {}
    for si, stratum in enumerate(STRATA):
        if stratum not in a.strata:
            continue
        for sd in sorted((pathlib.Path(a.eof_run) / stratum).glob("seed-*")):
            t0 = time.time(); k = int(sd.name.split("-")[1]); D = load(sd, compact); n = len(D["unix_s"])
            ok = np.isfinite(D["unix_s"]) & np.isfinite(D["latitude_deg"]) & np.isfinite(D["longitude_deg"]) & np.isfinite(D["kinetic_energy_j"])
            rec = np.zeros(n, DT); rec["row"] = np.arange(n); rec["parent"] = np.nan_to_num(D["parent"], nan=-1).astype(np.int64)
            rec["not_computed"] = (~ok).astype(np.uint8)
            imos = np.zeros(n); h = np.zeros(n)
            im, hh = m.soft(D["unix_s"][ok], D["latitude_deg"][ok], D["longitude_deg"][ok], D["kinetic_energy_j"][ok], [20261010, si, k])
            imos[ok] = im; h[ok] = hh
            rec["lnL_soft_imos"] = imos; rec["lnL_soft_h01w"] = h; rec["lnL_soft"] = imos + h; rec["lnL_gated"] = 0.0
            od = out / stratum / sd.name; od.mkdir(parents=True, exist_ok=True); f = od / "hydro-lnL.npy"; np.save(f, rec)
            (od / "COLUMNS.txt").write_text("\n".join(DT.names) + "\n")
            (od / "SHA256SUMS").write_text(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  hydro-lnL.npy\n")
            summ[f"{stratum}/{sd.name}"] = dict(rows=n, not_computed=int((~ok).sum()), lnL_soft_q=[float(np.quantile(rec["lnL_soft"][ok], q)) for q in (0.01, 0.5, 0.99)])
            print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s", flush=True)
    (out / "README.txt").write_text(__doc__ + "\nSummary per seed:\n" + json.dumps(summ, indent=1) + "\n")
    (out / "READY").write_text(f"hydroacoustics per-impact columns written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; "
                               "lnL_gated = 0.0 (module likelihood); lnL_soft exploratory; see README.txt\n")


if __name__ == "__main__":
    main()
