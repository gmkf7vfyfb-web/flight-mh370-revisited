"""Module review re-run of the hydroacoustic test of the Pleiades hypothesis (stand-in first pass, prereg c8b64a8).

PRE-REGISTERED AMENDMENT (Hydroacoustic Module, 10 Oct 2026), committed before this script is run. The stand-in's
scripts in this directory are copied unchanged from results/hydroacoustics-pleiades-test-standin/standin-scripts/
(lhyd.py sha256 5000c56e...). This file adds station terms; it changes nothing else.

WHY (module review, architecture.md ~19:50 and ~20:55 UTC): the stand-in's H01W term scores Kadri's Table 1 over
00:27-00:57 at every bearing, while its background density lambda comes from Table 1's own box (00:38:29-00:55:07,
234.67-343.16 deg). Coverage and lambda must describe the same search region.

TERMS COMPUTED PER ROW (same nuisance stream as the stand-in: default_rng([20261010, stratum_index, seed])):
  H01W-box   (NEW PRIMARY for H01W): q = P_D x [t_arr in 00:38:29-00:55:07] x [baz in 234.67-343.16]; lambda as the
             stand-in (18 / (998 s x 108.49 deg)).
  H01W-wide  (sensitivity): q over 00:27-00:57, every bearing; lambda = 18 / (1,800 s x 360 deg).
  H01W-standin: the stand-in's term, recomputed here as a check (must reproduce its per-seed sums to 1e-9 relative).
  *-bn       : the same three with IMS noise from Blackman 2004 (results-data/blackman_noise/blackman_noise_offsets.json:
             H01W SNR lowered by the H01W offset, +5.44 dB).
  IMOS       : the stand-in's IMOS terms, unchanged.
  Totals: A-box = IMOS + H01W-box (NEW HEADLINE), A-wide, A-standin, A-box-bn.
EVENT ATTRIBUTION: for each Table 1 event k, its posterior-weighted share of the matched H01W-box term,
  sum_i w_i q_i f_ik/lambda / L_i over rows, under flight weights and under H weights (w x L_P); the top 3 are reported
  for each option.
READING: unchanged from prereg c8b64a8 section 5 (|ln R| < 0.5 within noise; 0.5-1 weak; 1-2.3 moderate; > 2.3
  strong; +-2 sigma split-half band). The stand-in's result stands if A-box falls in the same band; otherwise the module
  result replaces it, with both reported.
AMENDMENT 1 (before any full run; the queued run was stopped before it started): P_D CEILING. The stand-in's
  logistic P_D(SNR) extrapolates far beyond the injected range (q -> 1 - 1e-28, so ln(1 - q) reaches -66 per row).
  The injections recover 200/200 at the highest SNR (40 dB), which supports P_D only up to about 0.98-0.995. Variants
  "*-cap" apply P_D <= 201/202 = 0.995 (posterior mean of Beta(1 + 200, 1 + 0)) at IMOS and H01W. A-box-cap becomes
  the NEW HEADLINE; A-box (uncapped) is kept beside it.
POWER CHECK: not re-run here (the stand-in's power check carries Kadri's term at its own coverage); if the headline band
  changes, the power check is re-run with the amended term before any reading is stated.

Usage: python review_rerun.py <module_dir> <imos_events.json> <kadri_table1.csv> <displacement_hist.py>
                              <end-of-flight/next-run> <pleiades hydro-test/next-run-b> <out_dir>
"""
import json, pathlib, sys, time
import numpy as np
from scipy.special import logsumexp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lhyd                # noqa: E402  (stand-in, unchanged)
import rhyd_result as RR   # noqa: E402  (stand-in, unchanged)

BOX_T = (38 * 60 + 29.0, 55 * 60 + 7.0)
BOX_B = (234.67, 343.16)
LAM_WIDE = 18.0 / (1800.0 * 360.0)


PD_CAP = 201.0 / 202.0


class ReviewModel(lhyd.Model):
    cap = None

    def _pd(self, snr, lg):
        p = lhyd.Model._pd(self, snr, lg)
        return np.minimum(p, self.cap) if self.cap is not None else p

    def review_terms(self, t_imp_unix, lat, lon, E, rng, h01w_offset_db):
        """IMOS terms as the stand-in; H01W in three coverage variants, each with and without the Blackman noise."""
        base = self.station_terms(t_imp_unix, lat, lon, E, rng, "A")      # consumes the same nuisance draws first
        n = len(lat); rng2 = np.random.default_rng(self._seed)            # replay the identical nuisance stream
        nu = self.nuisance(rng2, n); t0 = t_imp_unix - lhyd.DAY0_UNIX
        Cs = nu["c_site"] + nu["c_ims"]
        snr = self._snr0(lat, E, nu, self.tl_ims["H01W"], "3376") + Cs + lhyd.TRIAD_GAIN_DB
        baz, d = self.geometry(lat, lon, "H01W"); t_arr = t0 + d / lhyd.C_MEAN
        sd_t = np.sqrt(lhyd.PICK_S ** 2 + (d * lhyd.C_SD / lhyd.C_MEAN ** 2) ** 2)
        ev = self.kadri; out = {"IMOS": sum(base[lg] for lg in self.B.LOGGERS), "H01W-standin-orig": base["H01W"]}
        self.cap = PD_CAP
        basec = self.station_terms(t_imp_unix, lat, lon, E, np.random.default_rng(self._seed), "A")
        out["IMOS-cap"] = sum(basec[lg] for lg in self.B.LOGGERS)
        q_cap = np.minimum(self._pd(snr, "3274"), PD_CAP)
        self.cap = None
        attrib = None
        for tag, off in (("", 0.0), ("-bn", h01w_offset_db)):
            pdv = self._pd(snr - off, "3274")
            in_t_std = (t_arr >= lhyd.KADRI_SPAN[0]) & (t_arr <= lhyd.KADRI_SPAN[1])
            in_box = (t_arr >= BOX_T[0]) & (t_arr <= BOX_T[1]) & (baz >= BOX_B[0]) & (baz <= BOX_B[1])
            out[f"H01W-standin{tag}"] = np.log(self._mix(in_t_std * pdv, t_arr, sd_t, ev[:, 0], lhyd.KADRI_LAMBDA, baz, ev[:, 1]))
            q = in_box * pdv
            out[f"H01W-box{tag}"] = np.log(self._mix(q, t_arr, sd_t, ev[:, 0], lhyd.KADRI_LAMBDA, baz, ev[:, 1]))
            out[f"H01W-wide{tag}"] = np.log(self._mix(in_t_std * pdv, t_arr, sd_t, ev[:, 0], LAM_WIDE, baz, ev[:, 1]))
            if tag == "":
                L = np.exp(out["H01W-box"]); attrib = []
                for k in range(len(ev)):
                    lf = -0.5 * np.log(2 * np.pi * sd_t ** 2) - 0.5 * ((ev[k, 0] - t_arr) / sd_t) ** 2
                    db = (ev[k, 1] - baz + 180.0) % 360.0 - 180.0
                    attrib.append(q * np.exp(lf + self.K.log_t(db, lhyd.SD_BEAR, lhyd.NU_T)) / lhyd.KADRI_LAMBDA / L)
        in_box = (t_arr >= BOX_T[0]) & (t_arr <= BOX_T[1]) & (baz >= BOX_B[0]) & (baz <= BOX_B[1])
        out["H01W-box-cap"] = np.log(self._mix(in_box * q_cap, t_arr, sd_t, ev[:, 0], lhyd.KADRI_LAMBDA, baz, ev[:, 1]))
        for tag in ("", "-bn"):
            for v in ("box", "wide", "standin"):
                out[f"A-{v}{tag}"] = out["IMOS"] + out[f"H01W-{v}{tag}"]
        out["A-box-cap"] = out["IMOS-cap"] + out["H01W-box-cap"]
        return out, attrib


def main():
    mod, evj, kd, eofp, eofrun, plrun, outd = sys.argv[1:8]
    import importlib.util
    out = pathlib.Path(outd); out.mkdir(parents=True, exist_ok=True)
    m = ReviewModel(mod, evj, kd)
    off = json.loads((pathlib.Path(mod) / "results-data/blackman_noise/blackman_noise_offsets.json").read_text())["H01W"]
    spec = importlib.util.spec_from_file_location("eof_dh", eofp); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
    dh.SATCOM_CSV = pathlib.Path(eofp).resolve().parents[3] / "data" / "satcom-observations.csv"
    rows, att = [], {}
    for si, stratum in enumerate(RR.STRATA):
        for sd in sorted((pathlib.Path(eofrun) / stratum).glob("seed-*")):
            t0 = time.time(); k = int(sd.name.split("-")[1])
            meta = json.loads((sd / "run.json").read_text()); names = RR.needed(meta)
            data = RR.read_cols(sd / "impacts.npy", meta, names); n = len(data["weight"])
            store = RR.Store(data, {nm: meta["impact_columns"].index(nm) for nm in names}); dh.np = RR.NPProxy(store)
            g = lambda nm: data[nm]
            logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
            present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
            derived = dh.derived_logliks(meta, g, present)
            Pl = np.load(pathlib.Path(plrun) / stratum / sd.name / "pleiades-lnL.npy", mmap_mode="r")
            assert len(Pl) == n and np.array_equal(np.asarray(Pl["row"]), np.arange(n))
            lnLP = np.asarray(Pl["lnL_both_mean"], float); nc = np.asarray(Pl["not_computed"]).astype(bool)
            m._seed = [20261010, si, k]
            L, attrib = m.review_terms(data["unix_s"], data["latitude_deg"], data["longitude_deg"], data["kinetic_energy_j"],
                                       np.random.default_rng(m._seed), off)
            chk = float(np.max(np.abs(L["H01W-standin"] - L["H01W-standin-orig"])))
            got = {key: p for key, p, _c in dh.option_posteriors(sd, sd, constraints=("alive",)) if key in RR.BASE}
            for name, key in RR.OPTS.items():
                p = got[key]; lp = np.log(np.where(p > 0, p, np.nan)); lp = np.where(np.isfinite(lp), lp, -np.inf)
                b = RR.BASE[key]; base = derived[b] if b in derived else data["loglik:" + b]
                ll = np.where(np.isfinite(base), base, -np.inf) + dh.constraint_log_factor(g, logon, "other", "alive")
                with np.errstate(divide="ignore"):
                    lz = float(logsumexp(np.log(data["weight"]) + ll) - np.log(data["weight"].sum()))
                comp = ~nc & np.isfinite(lp); allr = np.isfinite(lp); lpH = lp + np.where(nc, -np.inf, lnLP)
                r = dict(stratum=stratum, si=si, seed=k, option=name, key=key, ln_Z0019=lz, check_standin_maxabs=chk,
                         lnS0=RR.lse_w(lp, np.zeros(n), allr), lnS0_comp=RR.lse_w(lp, np.zeros(n), comp), lnSH=RR.lse_w(lp, lnLP, comp))
                for v, lh in L.items():
                    if v == "H01W-standin-orig":
                        continue
                    r[f"lnS0L|{v}"] = RR.lse_w(lp, lh, allr); r[f"lnS0L_comp|{v}"] = RR.lse_w(lp, lh, comp); r[f"lnSHL|{v}"] = RR.lse_w(lp, lnLP + lh, comp)
                rows.append(r)
                wF = np.exp(lp - lp.max()); wF /= wF.sum(); wH = np.exp(np.where(comp, lpH, -np.inf) - lpH[comp].max()); wH /= wH.sum()
                a = att.setdefault(name, {"flight": np.zeros(len(attrib)), "H": np.zeros(len(attrib))})
                a["flight"] += RR_pi(stratum) / 4 * np.array([float(np.sum(wF * x)) for x in attrib])
                a["H"] += RR_pi(stratum) / 4 * np.array([float(np.sum(wH * x)) for x in attrib])
            print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s, standin check {chk:.1e}", flush=True)
            del data, store, L, attrib, got
            (out / "per_seed.json").write_text(json.dumps(rows, indent=1))
    ev = m.kadri
    attr = {name: {w: sorted([dict(t_s=float(ev[k, 0]), bearing=float(ev[k, 1]), share=float(v[w][k] / max(v[w].sum(), 1e-300)))
                              for k in range(len(ev))], key=lambda x: -x["share"])[:3] for w in ("flight", "H")} for name, v in att.items()}
    (out / "h01w_event_attribution.json").write_text(json.dumps(attr, indent=1))


_PF = None


def RR_pi(stratum):
    """Fixed P(family) for the attribution average only (core's, as the stand-in)."""
    global _PF
    if _PF is None:
        _PF = json.loads(pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/summary/mixture.json").read_text())["p_family"]
    return _PF[stratum]


if __name__ == "__main__":
    main()
