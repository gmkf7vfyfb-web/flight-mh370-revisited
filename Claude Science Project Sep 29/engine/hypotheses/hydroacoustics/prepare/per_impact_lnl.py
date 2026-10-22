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
AMENDMENT 2 (11 Oct 2026, PRE-REGISTERED before any run C row was scored; answers the architecture audit F4, F8 and
  the run C stratum names). Default for run C; the earlier behaviour stays behind --calerr flat --noise proxy.
  (a) --noise blackman (default): the H01W triad term uses Blackman App. B noise, i.e. the IMOS 3376 proxy + 5.44 dB
      (results-data/blackman_noise/blackman_noise_offsets.json). Was: the proxy alone.
  (b) --calerr structured (default): the frequency-flat C_site ~ N(0, 10 dB) is replaced by a per-band calibration
      error on TL, e_b = L + clip(S * log2(f_b / 25 Hz), -15, +15) dB, with L ~ N(0, 10 dB) (the same level spread
      as C_site: it carries the unconstrained transfer of eta between sites, audit F5) and S ~ N(0, 10.4 dB/octave)
      (the full air9 tilt at H01W, audit F1, taken zero-mean because about two thirds of it is array directivity that
      an impact does not share). Clipping at +/-15 dB is the explicit allowance below the data span (H01W < 12.5 Hz).
      e_b > 0 means more received signal. One (L, S) draw per row, shared by all stations (as C_site was). C_rcv and
      C_ims are unchanged. Label: "conditional on the calibration error model".
AMENDMENT 3 (11 Oct 2026 ~16:40 UTC, PRE-REGISTERED before its first run; architecture ruling 5 of 00:50 -0600):
  --tau eof uses end of flight's run C sidecars seed-k/tau90_v1.npz (impact_tau_method = 1, checked: method == 1) for
  the source duration, with the module's stage B mapping from mechanical to acoustic duration (agw_regime.py prereg):
  tau_ac = k * tau90, k drawn per row uniformly from {0.5, 1, 2} (stream rng([20261011, stratum, seed])); tau_ac is
  clamped to the eta_cal grid 0.05-10 s and the clamped share is reported. --tau-k 1 fixes k = 1 (the stand-in's
  choice, for a reproduction check). Default stays --tau scenario (log-uniform 0.05-10 s): the scenario tau is shown
  beside as the sensitivity, as the ruling asks. The nuisance stream for every other parameter is unchanged.
  Note (audit F7): S_b is normalised over 1-500 Hz and eta_cal(tau) is inverted at each tau, so tau is nearly a cancelled
  nuisance in this chain until coupling is calibrated on a second event with a different tau (G-H1). The
  convention is kept (it changes no prediction); it is stated in every label.
  LABELS carried in README (11 Oct): IMS P_D is BORROWED (IMOS 3274 logistic fit + 4.8 dB triad gain; audit F9);
      coupling has no angle/speed/breakup dependence and tau is drawn from the prior because end of flight's
      latent:energy_transfer_tau90_s is NaN in run C (coverage gap G-H1); TL NOT CALIBRATED (audit, rule C6):
      lnL_soft is a sensitivity only.
AMENDMENT 8 (17 Oct 2026, PRE-REGISTERED and committed before any run J row is scored; Pete 17 Oct: start the run J pass
  at 4 threads and expand as cores free; end of flight 20:41Z: run J inputs complete). Run J replaces run I and run-i-dive
  for downstream work (Pete, 15 Oct). Changes, all format or provenance; no likelihood formula changes:
  (a) Stratum directories run-<letter>-<family> (run J: run-j-waypoints, run-j-free, run-j-repro-radar, run-j-descent-climb)
      map to the canonical rng stratum index like next-<letter>-<family> (waypoints 4, free 0, repro-radar 1, descent-climb 2).
  (b) PRIMARY tau for run J is --tau eof: end of flight's tau90_v1.npz is on all 74 run J seeds (method == 1, asserted per
      seed), so coverage gap G-H1 is closed for run J. The k in {0.5, 1, 2} mechanical-to-acoustic mapping of amendment 3 is
      unchanged. --tau scenario is written to a separate output directory as the labelled SENSITIVITY.
  (c) Not used, declared: attitude_v1.npz (bank_source = 1 is wings level by model assumption, about 0.48-0.51 of rows;
      this chain's coupling has no attitude dependence, so attitude enters no value); n_pulses (= 1 for every row, declared
      single-pulse model, which this chain already assumes); the tau sidecar key w_steep (a regime-blend diagnostic, not a
      weight; end of flight 20:41Z). energy_transferred_j = contact kinetic energy is not read; KE is used as before.
  (d) Reporting only: the per-seed summary adds tl_lat_clamped_share, the share of computed rows whose latitude lies outside
      the TL table's latitude span and whose TL is therefore clamped to the nearest edge (whole-arc coverage, ARCHITECTURE
      rule 5 as revised 17 Oct). Such rows carry the label "TL clamped at the table edge (reach gap)".
  (e) Parallel workers: --part writes the per-invocation summary to <out>/_parts/<tag>.json and does NOT write README.txt or
      READY; a finaliser writes README.txt and READY once, after every seed is present and checked. No value changes.
  Labels carried unchanged from run I: TL NOT CALIBRATED; IMS P_D borrowed (IMOS 3274 + 4.8 dB); lnL_gated = 0.0 is the
  module likelihood; lnL_soft is a sensitivity only. Run J convergence: "accepted as a pass by project ruling, 16 Oct 2026".
  AMENDMENT 7 (12 Oct 2026): run I stratum next-i-waypoints maps to rng stratum index 4 (new; nuisance stream only).
  AMENDMENT 6 (11 Oct 2026): stratum names next-<letter>-<family> accepted (run D-he); no value changes.
  AMENDMENT 5 (11 Oct 2026, labels only; no computed value changes): H08S on 8 March 2014 is contaminated by periodic
      impulses about every 10-15 s (Kadri 2024 Fig. 9d-e; kadri_fig9_noise, 3b539351): masking/false alarms not
      modelled; H01W March 2014 noise reads -6 dB vs Blackman 2003 from Kadri's spectrogram colours (time series agree
      with Blackman): sensitivity only; H08N is BLOCKED for MH370 impacts even in the N x 2D corridor (K4); ridge paths
      that cut the sound-channel axis are a reach gap (G-N2, K5).
  (c) Run C stratum directories are named next-c-<family>; they map to core's order (free, repro-radar,
      descent-climb, routes) for the rng stratum index. --strata is now honoured (it was parsed but ignored).

AMENDMENT 9 (22 Oct 2026, work order 2026-10-21 block 2; committed before any run J row is scored with it). --tl-table
  arc-grid replaces the five-quantile TL latitude tables (38.46-31.64 S, clamped outside) by the whole-arc grid tables
  results-data/tl_grid_run_j/{ims_tl_kraken_arc.csv, imos_tl_ramcorr_arc.csv} (41-20 S, offset-0 arc line; tl_grid_table.py
  states the interpolation rule: linear in latitude, clamped at 41 S and 20 S, blocked bands NaN -> zero energy). The RAM
  deltas are applied exactly as before (IMS: lhyd rule from ims_ram_delta.csv; IMOS: inside the table). Default stays
  --tl-table quantile5 (no value changes to anything already written); the arc-grid tables are the drop-in for block 3,
  which closes the reach gap "TL clamped at the table edge" for rows between 41 S and 20 S. Receivers without a RAM
  delta (H08N, 3250) are in the grid tables but are not scored by this chain (unchanged).

Usage (from prepare/, PYTHONPATH=.:exploratory/pleiades_test):
  python per_impact_lnl.py <module_dir> <eof_run_dir> <out_dir> <kadri_table1.csv> [--compact-reader <compact_impacts.py>]
"""
# AMENDMENT 4 (11 Oct 2026, audit F10; written before its smoke run). The H01W triad noise (Blackman App. B, a SAC
#   amplitude-spectrum conversion inferred from legend file names, May-June 2003) carries a +/-3 dB conversion
#   uncertainty: noise_err ~ N(0, --noise-sd dB) per row, default 3, drawn from its OWN stream (seed-derived) so every
#   other nuisance draw is unchanged; SNR -= noise_err. --noise-sd 0 reproduces amendment 3 exactly. Label added:
#   Fix before any amendment-4 result (crash: seed may itself be a sequence): stream = rng(flat(seed) + [4]).
#   "noise from May-June 2003 (season differs from March 2014), +/-3 dB conversion". lnL_gated is unaffected (0.0).
import argparse, hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "exploratory" / "pleiades_test"))
import lhyd                    # noqa: E402  stand-in, unchanged
import review_rerun as RV      # noqa: E402  module amendment (H01W box)

STRATA = ["next-free", "next-repro-radar", "next-descent-climb", "next-routes"]
DT = np.dtype([("row", "<i8"), ("parent", "<i8"), ("lnL_gated", "<f8"), ("lnL_soft", "<f8"), ("lnL_soft_imos", "<f8"),
               ("lnL_soft_h01w", "<f8"), ("not_computed", "u1")])


BN_OFF = json.loads((HERE.parent / "results-data/blackman_noise/blackman_noise_offsets.json").read_text())
CANON = {"free": 0, "repro-radar": 1, "descent-climb": 2, "routes": 3, "waypoints": 4}   # waypoints: amendment 7 (run I)


def stratum_index(name):
    import re   # amendment 6 (11 Oct): run D-he strata are next-d-<family>; any next-<letter>- prefix is stripped
    return CANON[re.sub(r"^(?:next|run)-(?:[a-z]-)?", "", name)]   # amendment 8(a): run-<letter>- accepted


class Terms(RV.ReviewModel):
    calerr = "structured"
    noise = "blackman"
    tau_override = None      # per-row tau_ac (amendment 3), set by main() for the current seed
    noise_sd = 3.0           # amendment 4 (audit F10)

    def nuisance(self, rng, n):
        nu = lhyd.Model.nuisance(rng, n)
        if self.tau_override is not None:
            assert len(self.tau_override) == n
            nu["tau"] = self.tau_override.copy()
        if self.calerr == "structured":
            r2 = np.random.default_rng(rng.integers(0, 2 ** 63))
            nu["cal_L"], nu["cal_S"] = r2.normal(0, 10, n), r2.normal(0, 10.4, n)
            nu["c_site"] = np.zeros(n)
        return nu

    def _se(self, lat, E, nu, tab):
        if "cal_L" not in nu:
            return lhyd.Model._se(self, lat, E, nu, tab)
        F, B = self.F, self.B
        n = len(lat); eta = np.zeros(n)
        for z, (lx, ly) in self.etab.items():
            m = nu["zs"] == z; eta[m] = 10 ** np.interp(np.log10(nu["tau"][m]), lx, ly)
        SE1 = eta * E * B.RHO_C / (2 * np.pi)
        ltau = np.log10(nu["tau"]); SE = np.zeros(n); la = np.clip(lat, self.xs.min(), self.xs.max())
        for fc in F.BANDS:
            sb = np.interp(ltau, np.log10(lhyd.TAU_GRID), self.Sb[fc]); tlb = np.zeros(n)
            for z in F.SRC:
                mz = nu["zs"] == z; tlb[mz] = np.interp(la[mz], self.xs, tab[(fc, z)])
            e_b = nu["cal_L"] + np.clip(nu["cal_S"] * np.log2(fc / 25.0), -15.0, 15.0)
            SE += SE1 * sb * np.nan_to_num(10 ** (-(tlb - e_b) / 10), nan=0.0)
        return SE

    def soft(self, t_unix, lat, lon, E, seed):
        self.cap = RV.PD_CAP
        rng = np.random.default_rng(seed)
        base = self.station_terms(t_unix, lat, lon, E, rng, "A")
        n = len(lat); nu = self.nuisance(np.random.default_rng(seed), n); t0 = t_unix - lhyd.DAY0_UNIX
        snr = self._snr0(lat, E, nu, self.tl_ims["H01W"], "3376") + nu["c_site"] + nu["c_ims"] + lhyd.TRIAD_GAIN_DB
        if self.noise == "blackman":
            snr = snr - BN_OFF["H01W"]
        if self.noise_sd > 0:   # amendment 4: own stream, other draws unchanged
            snr = snr - np.random.default_rng([int(v) for v in np.ravel(seed)] + [4]).normal(0.0, self.noise_sd, n)
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
    ap.add_argument("--calerr", choices=["structured", "flat"], default="structured")
    ap.add_argument("--noise", choices=["blackman", "proxy"], default="blackman")
    ap.add_argument("--tau", choices=["scenario", "eof"], default="scenario"); ap.add_argument("--tau-k", type=float)
    ap.add_argument("--seeds", nargs="+", type=int)
    ap.add_argument("--noise-sd", type=float, default=3.0)   # amendment 4
    ap.add_argument("--part")   # amendment 8(e): parallel worker tag; no README/READY
    ap.add_argument("--tl-table", choices=["quantile5", "arc-grid"], default="quantile5")   # amendment 9
    ap.add_argument("--tl-table-dir", default=str(HERE.parent / "results-data/tl_grid_run_j"))
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    compact = None
    if a.compact_reader:
        spec = importlib.util.spec_from_file_location("compact_impacts", a.compact_reader); compact = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(pathlib.Path(a.compact_reader).parent)); spec.loader.exec_module(compact)
    Terms.calerr, Terms.noise, Terms.noise_sd = a.calerr, a.noise, a.noise_sd
    m = Terms(a.module_dir, a.imos_events, a.kadri_csv); summ = {"options": dict(calerr=a.calerr, noise=a.noise, tau=a.tau, tau_k=a.tau_k, noise_sd=a.noise_sd, tl_table=a.tl_table)}
    if a.tl_table == "arc-grid":   # amendment 9
        import tl_grid_table as TT
        summ["options"]["tl_table_dir"] = a.tl_table_dir; summ["options"]["tl_span_deg"] = TT.apply_to_model(m, a.tl_table_dir)
    for stratum in a.strata:
        si = stratum_index(stratum)
        for sd in sorted(d for d in (pathlib.Path(a.eof_run) / stratum).glob("seed-*") if d.is_dir()
                         and (a.seeds is None or int(d.name.split("-")[1]) in a.seeds)):  # bug fix 11 Oct: run C has seed-k.convert8.log files
            t0 = time.time(); k = int(sd.name.split("-")[1]); D = load(sd, compact); n = len(D["unix_s"])
            ok = np.isfinite(D["unix_s"]) & np.isfinite(D["latitude_deg"]) & np.isfinite(D["longitude_deg"]) & np.isfinite(D["kinetic_energy_j"])
            rec = np.zeros(n, DT); rec["row"] = np.arange(n); rec["parent"] = np.nan_to_num(D["parent"], nan=-1).astype(np.int64)
            rec["not_computed"] = (~ok).astype(np.uint8)
            imos = np.zeros(n); h = np.zeros(n)
            m.tau_override = None; clamp = None
            if a.tau == "eof":
                z = np.load(sd / "tau90_v1.npz"); assert int(z["method"]) == 1, "tau90 sidecar is not impact_tau_method = 1"
                t90 = z["tau90_s"].astype(float)[ok]
                kk = np.full(len(t90), a.tau_k) if a.tau_k else np.random.default_rng([20261011, si, k]).choice([0.5, 1.0, 2.0], len(t90))
                tac = kk * t90; clamp = float(np.mean((tac < lhyd.TAU_GRID[0]) | (tac > lhyd.TAU_GRID[-1])))
                m.tau_override = np.clip(tac, lhyd.TAU_GRID[0], lhyd.TAU_GRID[-1])
            im, hh = m.soft(D["unix_s"][ok], D["latitude_deg"][ok], D["longitude_deg"][ok], D["kinetic_energy_j"][ok], [20261010, si, k])
            imos[ok] = im; h[ok] = hh
            rec["lnL_soft_imos"] = imos; rec["lnL_soft_h01w"] = h; rec["lnL_soft"] = imos + h; rec["lnL_gated"] = 0.0
            od = out / stratum / sd.name; od.mkdir(parents=True, exist_ok=True); f = od / "hydro-lnL.npy"; np.save(f, rec)
            (od / "COLUMNS.txt").write_text("\n".join(DT.names) + "\n")
            (od / "SHA256SUMS").write_text(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  hydro-lnL.npy\n")
            summ[f"{stratum}/{sd.name}"] = dict(rows=n, not_computed=int((~ok).sum()), lnL_soft_q=[float(np.quantile(rec["lnL_soft"][ok], q)) for q in (0.01, 0.5, 0.99)], tau_clamped_share=clamp)
            la_ = D["latitude_deg"][ok]   # amendment 8(d): reporting only
            summ[f"{stratum}/{sd.name}"]["tl_lat_clamped_share"] = float(np.mean((la_ < m.xs.min()) | (la_ > m.xs.max()))) if len(la_) else None
            print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s", flush=True)
    if a.part:   # amendment 8(e)
        (out / "_parts").mkdir(exist_ok=True); (out / "_parts" / f"{a.part}.json").write_text(json.dumps(summ, indent=1) + "\n")
        return
    (out / "README.txt").write_text(__doc__ + "\nSummary per seed:\n" + json.dumps(summ, indent=1) + "\n")
    (out / "READY").write_text(f"hydroacoustics per-impact columns written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; "
                               "lnL_gated = 0.0 (module likelihood); lnL_soft exploratory; see README.txt\n")


if __name__ == "__main__":
    main()
