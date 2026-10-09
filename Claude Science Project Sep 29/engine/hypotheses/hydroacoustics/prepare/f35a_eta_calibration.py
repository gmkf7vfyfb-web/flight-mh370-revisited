"""PRE-REGISTRATION and implementation: calibrate this module's coupling efficiency eta on the F-35A
(JASDF 79-8705, 9 Apr 2019) -> H11 path (part 1), then re-map stage B with the calibrated eta (part 2,
'stage C'). Committed BEFORE any transmission loss on the F-35A paths is computed.

WHY: stage B (imos_stageB_tl.py, 64752c7) anchors eta at 2.1e-4, Brown et al. (2026, p. 17) through Arons'
explosive law (an equivalent-yield coupling), whereas the module's eta is the fraction of impact energy
radiated as acoustic energy into the water (SE_1m = eta E rho c / 2 pi, physics.rs). Part 1 measures the
module's own eta on the one aircraft impact with a published far-field level, through the same engine.

PART 1 (calibration)
  Source: 40.64 N 142.96 E, the module's working point derived from Metz, Obana & Fukao 2023, p. 1348 (the
     epicentre falls within 8 km of the 135 km range circle from Misawa; 40.54-40.72 N across that band;
     results/hydroacoustics-references.md), 10:26:32 UTC 9 Apr 2019. Kadri's S1 coordinates are not used.
  Paths: shared ocean transport export f35a-H11S, f35a-H11N (merge 61b50a5; GEBCO_2026 + NW Pacific layer,
     WOA23 B5C2 April, soundspeed_nwpac), converted by shared_paths.convert.
  TL: identical to stage B - KRAKEN adiabatic incoherent modes (kraken_tl.py), profiles every 5 km
     (air9_tl_validation.build_profiles), HARD bottom, Francois-Garrison, spherical correction; third
     octaves 5-40 Hz (10 bands); source depths 2, 10, 30 m. Receiver: the triad's mean hydrophone depth
     (data/stations.csv: H11N 730.7 m, H11S 739.3 m), a SOFAR-axis receiver of the kind air9 validated.
  Observation: peak pressure 0.7 Pa at H11 (Brown et al. 2026, p. 17). Brown names neither the triad nor
     the band: applied to both H11N and H11S (both reported; their mean in log eta is primary) and taken as
     the 5-40 Hz peak. If Brown's 0.7 Pa is broader-band, the in-band peak is smaller and eta_cal is BIASED
     HIGH (disclosed; the bias favours detectability).
  Peak-to-exposure ratio R = p_pk^2 / SE (1/s), measured on the stage-A templates at 3315 (T_C2 primary,
     T_C1 alternative): 5-40 Hz band-passed (4th-order Butterworth, zero phase), SE = noise-subtracted
     energy as in imos_stageB_map.t_eff, p_pk = max |band-passed signal| (not noise-corrected; the
     templates have 19.2 and 14.5 dB SNR). Ratios cancel the logger calibration (in-band gain variation
     disclosed). R is a property of far-field SOFAR arrivals at 2,400-5,000 km, as H11 is at 3,341 km.
  Inversion: SE_obs = 0.7^2 / R; SE_mod(eta) = eta E rho c / (2 pi) sum_b S_b(tau, slope) 10^(-TL_b/10),
     with S_b = imos_stageB_map.band_fraction; hence eta_cal = SE_obs / SE_mod(1). No C_site, no C_rcv:
     eta_cal is an EFFECTIVE eta (eta x site term) for a near-vertical fast-jet impact seen at a SOFAR
     receiver. E = 900 MJ (Brown, p. 17; 700 and 1100 MJ as the reported range).
  Grid: tau 0.05-10 s (25 log-spaced points), slope 2 (primary) and 4, source depth, station, template, E.
  Outputs: <out>/f35a_tl.csv, <out>/eta_cal.csv, <out>/eta_cal_summary.json (median and range of log10
     eta_cal over z_s x station x template x E at each tau and slope; comparison with 2.1e-4 stated as a
     comparison between DIFFERENT definitions).

PART 2 (stage C: stage B with the calibrated eta)
  Exactly imos_stageB_map.main (same seed 20261009, same draws, same prior, coverage, TL, T_eff, fits)
  except: eta_i = eta_cal(tau_i, slope, z_s,i; station mean, template T_C2, E = 900 MJ) x 10^(C_site,i/10),
  where C_site ~ N(0, 10 dB) is now the TRANSFER term (F-35A near-vertical at ~1,100 km/h to MH370; one
  term, not added twice), and C_rcv ~ N(0, 10 dB) is kept (seabed receivers vs the SOFAR-axis
  calibration). The eta prior of stage B is replaced, not combined. E_imp for MH370 as stage B (2e5 kg,
  V in {120, 160, 200} m/s). Outputs: <out>/stageC_pd_summary.csv, stageC_pd_by_latitude.csv.
  Reading: stage C remains a LOWER BOUND for the IMOS seabed receivers (adiabatic up-slope TL), and the
  calibration inherits Brown's 0.7 Pa (unrefereed preprint value, no H11 waveform published).

Usage: python f35a_eta_calibration.py <f35a_export_dir> <at_dir> <out_dir> <imos_tl.csv> <stageA summary.json>
       <stand-in summary json>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import air9_tl_validation as A  # noqa: E402
import imos_detectors as D  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402
import imos_stageB_map as B  # noqa: E402
import kraken_tl as K  # noqa: E402
import shared_paths as SP  # noqa: E402

HERE = Path(__file__).parent.parent
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
SRC = [2.0, 10.0, 30.0]
STATIONS = ["H11S", "H11N"]
P_PK = 0.7
E_F35 = {"low": 700e6, "mid": 900e6, "high": 1100e6}
TAUS = np.logspace(np.log10(0.05), 1.0, 25)


def receiver_depth(st):
    s = pd.read_csv(HERE / "data/stations.csv", comment="#")
    return float(s[s.triad == st].hydrophone_depth_m.mean())


def f35a_tl(exp, at_bin, out):
    stub = out / "stubschema"
    stub.mkdir(parents=True, exist_ok=True)
    rows = []
    for st in STATIONS:
        SP.convert(Path(exp), stub, f"f35a-{st}")
        bathy = pd.read_csv(stub / f"bathy_f35a_{st}.csv")
        ssp = pd.read_csv(stub / f"ssp_f35a_{st}.csv")
        rprof, profiles = A.build_profiles(bathy, ssp)
        rd = receiver_depth(st)
        assert rd < profiles[-1][0], (st, rd, profiles[-1][0])
        t0 = time.time()
        for fc in BANDS:
            tag = f"f{fc:g}".replace(".", "p")
            r, tl, nm, dt = K.tl_path(out / "work" / st, tag, fc, profiles, rprof, np.array([rprof[-1]]), SRC, [rd],
                                      A.BOTTOMS["hard"], at_bin, fg=A.FG)
            s = K.read_shd(out / "work" / st / f"{tag}.shd")
            x = s["rr_m"] / 1000.0 / 6371.0
            sph = 10 * np.log10(x / np.sin(x))
            for js, zs in enumerate(s["sz"]):
                tlz = -20 * np.log10(np.abs(s["p"][0, js, 0])) + sph
                rows.append(dict(station=st, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(rprof[-1]),
                                 tl_db=float(tlz[-1]), n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1))
        print(st, round(time.time() - t0, 1), "s", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "f35a_tl.csv", index=False)
    return df


def peak_ratio():
    """R = p_pk^2 / SE (1/s) on the stage-A templates at 3315, 5-40 Hz."""
    from scipy import signal
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=N.FS_D, output="sos")
    out = {}
    for name, hms in [("T_C2", "05:03:01"), ("T_C1", "01:33:44")]:
        t = D.DAY0 + pd.Timedelta(hms)
        for _, r in recs[recs.logger == 3315].iterrows():
            f = P.IMOS / r.file
            t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
            t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta["3315"], t0))
            s = (t - t0).total_seconds()
            xd = N.decimate(N.read_volts(f))
            if 10 <= s <= len(xd) / N.FS_D - 50:
                y = signal.sosfiltfilt(sos, xd[int((s - 10) * N.FS_D): int((s + 50) * N.FS_D)])
                e1 = (y[: len(y) // N.FS_D * N.FS_D] ** 2).reshape(-1, N.FS_D).sum(1) / N.FS_D
                se = float(np.clip(e1 - np.median(e1[:8]), 0, None).sum())
                out[name] = dict(R_per_s=float(np.max(np.abs(y[8 * N.FS_D:])) ** 2 / se), se_v2s=se)
                break
    return out


def calibrate(tl, R):
    rows = []
    rho_c = B.RHO_C
    for slope in [2, 4]:
        Sb = {fc: B.band_fraction(fc, 1 / TAUS, slope) for fc in BANDS}
        for (st, zs), g in tl.groupby(["station", "src_depth_m"]):
            g = g.set_index("fc_hz").tl_db
            gain = sum(Sb[fc] * 10 ** (-g[fc] / 10) for fc in BANDS)       # per tau
            for tn, rr in R.items():
                se_obs = P_PK ** 2 / rr["R_per_s"]
                for ek, E in E_F35.items():
                    eta = se_obs / (E * rho_c / (2 * np.pi) * gain)
                    for tau, e in zip(TAUS, eta):
                        rows.append(dict(slope=slope, station=st, src_depth_m=zs, template=tn, E_case=ek, tau_s=float(tau), eta_cal=float(e)))
    return pd.DataFrame(rows)


def summarise(cal):
    out = {}
    for (slope, tau), g in cal.groupby(["slope", "tau_s"]):
        le = np.log10(g.eta_cal)
        prim = g[(g.template == "T_C2") & (g.E_case == "mid")].groupby("src_depth_m").eta_cal.apply(lambda v: float(10 ** np.log10(v).mean()))
        out[f"{slope}|{tau:.4g}"] = dict(log10_median=float(le.median()), log10_min=float(le.min()), log10_max=float(le.max()),
                                         primary_by_src_depth={str(k): v for k, v in prim.items()})
    return out


def eta_cal_lookup(cal, slope):
    """Primary eta_cal(tau, z_s): station mean in log, T_C2, E = 900 MJ."""
    g = cal[(cal.slope == slope) & (cal.template == "T_C2") & (cal.E_case == "mid")]
    tab = {}
    for zs, h in g.groupby("src_depth_m"):
        m = h.groupby("tau_s").eta_cal.apply(lambda v: np.log10(v).mean())
        tab[float(zs)] = (np.log10(m.index.values), m.values)
    return tab


def stage_c(out, cal, tl_csv, sa_json, summary):
    """imos_stageB_map.main with eta replaced by eta_cal(tau, z_s) x 10^(C_site/10) (docstring PART 2)."""
    tl = pd.read_csv(tl_csv, dtype={"quantile": str, "logger": str})
    fits = json.loads(Path(sa_json).read_text())["fits"]
    bmed = json.loads((HERE / "results-data/imos2b/summary.json").read_text())["background_spl_median"]
    meta = P.parse_meta()
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    teff = B.t_eff(meta, recs, None)
    req = json.loads((HERE / "data/ocean_paths/request.json").read_text())
    qlat = {p["name"][3:6]: p["a"][1] for p in req["paths"] if p["name"].startswith("imp")}
    rng = np.random.default_rng(B.SEED)
    ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
    q, _ = P.sct.fit_small_circle(ridge)
    pr = P.sct.draw_prior(np.random.default_rng(P.sct.SEED), q, grid, dens, B.N_S, P.sct.BASE["sigma_x_nm"])
    n = len(pr)
    t_imp = P.sct.BASE["mu_t_s"] + rng.normal(0, P.sct.BASE["sigma_t_s"], n)
    c = rng.normal(P.C_G, P.SD_C, n)
    eta_b = 10 ** rng.uniform(np.log10(B.ETA_LO), np.log10(B.ETA_HI), n)   # drawn to keep the stream identical; unused
    tau = 10 ** rng.uniform(np.log10(0.05), np.log10(10), n)
    V = rng.choice([120.0, 160.0, 200.0], n)
    zs = rng.choice([2.0, 10.0, 30.0], n)
    c_site, c_rcv = rng.normal(0, 10, n), rng.normal(0, 10, n)
    del eta_b
    bands = sorted(tl.fc_hz.unique())
    fr = 1 / tau
    ref = (P.T_IMPACT_REF - D.DAY0).total_seconds()
    qs = sorted(qlat, key=lambda k: qlat[k])
    rows, lat_rows = [], []
    for slope in [2, 4]:
        tab = eta_cal_lookup(cal, slope)
        eta = np.zeros(n)
        for z, (lx, ly) in tab.items():
            m = zs == z
            eta[m] = 10 ** np.interp(np.log10(tau[m]), lx, ly)
        SE1 = eta * 0.5 * B.M_REF * V ** 2 * B.RHO_C / (2 * np.pi)
        Sb = {fc: B.band_fraction(fc, fr, slope) for fc in bands}
        p_none = {k: np.ones(n) for k in ["or@0.005|T_C2", "or@0.05|T_C2", "or@0.005|T_C1"]}
        snr_max = np.full(n, -np.inf)
        for lg in B.LOGGERS:
            m = meta[lg]
            _, _, d = P.GEOD.inv(np.full(n, m["lon"]), np.full(n, m["lat"]), pr[:, 1], pr[:, 0])
            ta = ref + t_imp + d / 1000 / c
            r = recs[recs.logger == int(lg)]
            st = np.array([((t + pd.Timedelta(seconds=D.subsec(P.IMOS / f))) - pd.Timedelta(seconds=P.clock_err(m, t)) - D.DAY0).total_seconds()
                           for t, f in zip(r.start_logger, r.file)])
            cov = np.zeros(n, bool)
            for a, b in zip(st + 32, st + r.dur_s.values - 1):
                cov |= (ta >= a) & (ta <= b)
            SE = np.zeros(n)
            for fc in bands:
                tlb = np.zeros(n)
                for z in SRC:
                    g = tl[(tl.logger == lg) & (tl.fc_hz == fc) & np.isclose(tl.src_depth_m, z)].set_index("quantile").tl_db
                    xs = np.array([qlat[k] for k in qs])
                    ys = np.array([g[k] for k in qs])
                    mz = zs == z
                    tlb[mz] = np.interp(pr[mz, 0], xs, ys)
                SE += SE1 * Sb[fc] * np.nan_to_num(10 ** (-tlb / 10), nan=0.0)
            SE *= 10 ** ((c_site + c_rcv) / 10)
            for key in p_none:
                det, tn = key.split("|")
                dname, a = det.split("@")
                f = fits[f"{B.TARGET[lg]}|{tn}|{dname}|{float(a)}"]
                spl = 10 * np.log10(np.maximum(SE, 1e-300) / teff[tn] / 1e-12)
                snr = spl - (bmed[lg] if lg in bmed else bmed[str(int(lg))])
                if key == "or@0.005|T_C2":
                    snr_max = np.maximum(snr_max, snr)
                s = max((f["snr90"] - f["snr50"]) / np.log(9), 0.05)
                p_none[key] *= 1 - cov * (1 / (1 + np.exp(-(snr - f["snr50"]) / s)))
        for key, pn in p_none.items():
            pdany = 1 - pn
            rows.append(dict(slope=slope, curve=key, pd_marginal=float(pdany.mean()),
                             eta_median=float(np.median(eta)), eta_p05=float(np.quantile(eta, 0.05)), eta_p95=float(np.quantile(eta, 0.95)),
                             snr_best_logger_median_db=float(np.median(snr_max)), snr_best_logger_p95_db=float(np.quantile(snr_max, 0.95))))
            for lo in np.arange(np.floor(pr[:, 0].min()), pr[:, 0].max(), 1.0):
                mm = (pr[:, 0] >= lo) & (pr[:, 0] < lo + 1)
                if mm.sum() > 500:
                    lat_rows.append(dict(slope=slope, curve=key, lat_bin=f"{lo:.1f}", pd=float(pdany[mm].mean())))
    pd.DataFrame(rows).to_csv(out / "stageC_pd_summary.csv", index=False)
    pd.DataFrame(lat_rows).to_csv(out / "stageC_pd_by_latitude.csv", index=False)
    return pd.DataFrame(rows)


def main(exp, at_bin, out_dir, tl_csv, sa_json, summary):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tl = f35a_tl(exp, at_bin, out)
    R = peak_ratio()
    cal = calibrate(tl, R)
    cal.to_csv(out / "eta_cal.csv", index=False)
    (out / "eta_cal_summary.json").write_text(json.dumps(dict(peak_ratio=R, p_pk_pa=P_PK, E_j=E_F35, by_slope_tau=summarise(cal)), indent=1))
    print(json.dumps(R, indent=1))
    print(stage_c(out, cal, tl_csv, sa_json, summary).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:7])
