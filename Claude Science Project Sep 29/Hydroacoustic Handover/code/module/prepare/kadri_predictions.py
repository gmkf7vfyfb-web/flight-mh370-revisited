"""Package for Kadri (brief section 9): predictions.csv on end-of-flight impacts. DRAFT for Pete's review; nothing is sent.

Not a test: a prediction table. One row per option x station x location bin (0.5 deg), for the bins that hold 99 % of
each option's weight.

IMPACTS AND WEIGHTS: end-of-flight next-run (core (b)), 4 strata x 4 seeds; weights from end of flight's own
`option_posteriors` (read-only, by path), variant `+alive` (transmitting at 00:19:37; ruling ~19:10 B, variant (a));
strata mixed by core's P(family), held fixed (mixture.json). Options: the core set 1-3 under the plain names
(ruling ~16:30): 00:19 Held Out, 00:19 R600 BTO Only, 00:19 R600 BTO + Raw BFO, log-on cause `other`. Holland H1/H2:
not yet estimable - targeted sampler in progress; not included.
PER BIN: weight; GEBCO_2026 seafloor depth at the bin centre (agw_regime.depth_at, 3x3 median); impact-time 5/50/95 %
  (30 s histogram); weighted mean kinetic energy (total and vertical).
PER STATION (H01W, H08S, H08N triad centroids): WGS84 range and back-azimuth from the station to the bin centre;
  SOFAR arrival window = [impact q05 + d/(c+2 sd), impact q95 + d/(c-2 sd)], c = 1.482 +- 0.006 km/s.
  TL per third-octave band 5-40 Hz, source depth 10 m: KRAKEN on the module's five impact-quantile paths minus the RAM
  correction of the median path (results-data/near_limits), interpolated in latitude and clamped outside 38.46-31.64 S
  (as near_limits_eof289.py). TL sd = 7.9 dB for every band: the RMS residual of the Blackman air9 validation
  (hydroacoustics-blackman-validation.md). H08N: TL not computed (the paths are blocked by the Great Chagos Bank).
  Blockage flag: station-level, from data/kadri_package/windows.csv (shared-transport ocean paths).
  Predicted exposure SE (Pa^2 s, 5-40 Hz) and peak pressure (Pa) for eta in {1e-4, 1e-3, 2.7e-3, 1e-2}:
    SE = eta * KE * rho c / 2 pi * sum_b S_b(tau) 10^(-TL_b/10), tau = 1 s, f^-2 roll-off (imos_stageB_map.band_fraction);
    p_pk = sqrt(R * SE), R = 3.013 /s (stage-A template T_C2, results-data/f35a_cal/eta_cal_summary.json).
    2.7e-3 is the F-35A RAM-corrected median eta_cal (hydroacoustics-ram-tl-check.md).
LABELS: core (b) split-half NOT converged; two-tank bookkeeping only; P(family) held fixed; uncorrected fuel;
  provisional sampler; PROVISIONAL; DRAFT for Pete's review.

Usage (from prepare/, PYTHONPATH=.):
  python kadri_predictions.py <end-of-flight/next-run> <summary/mixture.json> <displacement_hist.py> <out_dir>
"""
import csv, hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import search_windows as sw          # noqa: E402
import agw_regime as AG              # noqa: E402
import imos_stageB_map as B          # noqa: E402

OPTIONS = [("00:19 Held Out", "none__other+alive"), ("00:19 R600 BTO Only", "r600-bto__other+alive"),
           ("00:19 R600 BTO + Raw BFO", "r600_no-offset__other+alive")]
STATIONS = ["H01W", "H08S", "H08N"]
BIN = 0.5
T0 = 1394236800.0                    # 2014-03-08 00:00:00 UTC
TB = np.arange(0.0, 3 * 3600.0 + 1, 30.0)
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
ETAS = [1e-4, 1e-3, 2.7e-3, 1e-2]
TAU, ZS, TL_SD = 1.0, 10.0, 7.9
QS = ["025", "250", "500", "750", "975"]


def main(exch, mixjson, eofmod, out):
    from pyproj import Geod
    import pandas as pd
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); here = pathlib.Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("eof_dh", eofmod); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
    dh.SATCOM_CSV = pathlib.Path(eofmod).resolve().parents[3] / "data" / "satcom-observations.csv"
    PF = json.load(open(mixjson))["p_family"]; keys = {k for _, k in OPTIONS}
    acc = {k: {} for k in keys}       # key -> (ilat, ilon) -> [w, wKE, wVKE, hist]
    for stratum, Ps in PF.items():
        sds = sorted(d for d in (pathlib.Path(exch) / stratum).glob("seed-*") if (d / "impacts.npy").exists())
        for sd in sds:
            t0 = time.time(); meta = json.loads((sd / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
            X = np.load(sd / "impacts.npy", mmap_mode="r")
            t = np.asarray(X[:, cols["unix_s"]], float); la = np.asarray(X[:, cols["latitude_deg"]], float)
            lo = np.asarray(X[:, cols["longitude_deg"]], float)
            ke = np.asarray(X[:, cols["kinetic_energy_j"]], float); vke = np.asarray(X[:, cols["vertical_kinetic_energy_j"]], float)
            ok = np.isfinite(t) & np.isfinite(la) & np.isfinite(lo)
            for key, p, _c in dh.option_posteriors(sd, sd, constraints=("alive",)):
                if key not in keys:
                    continue
                w = np.where(ok, p, 0.0); w = w / w.sum() * Ps / len(sds); m = w > 0
                il = np.floor(la[m] / BIN).astype(int); jl = np.floor(lo[m] / BIN).astype(int)
                tb = np.clip(np.searchsorted(TB, t[m] - T0) - 1, 0, len(TB) - 2)
                ww, kk, vv = w[m], np.nan_to_num(ke[m]), np.nan_to_num(vke[m])
                cid = (il.astype(np.int64) + 1000) * 10000 + (jl + 1000)
                u, inv = np.unique(cid, return_inverse=True)
                sw_ = np.bincount(inv, ww); sk = np.bincount(inv, ww * kk); sv = np.bincount(inv, ww * vv)
                h = np.zeros((len(u), len(TB) - 1)); np.add.at(h, (inv, tb), ww)
                A = acc[key]
                for n_, c_ in enumerate(u):
                    kij = (int(c_ // 10000) - 1000, int(c_ % 10000) - 1000)
                    if kij not in A:
                        A[kij] = [0.0, 0.0, 0.0, np.zeros(len(TB) - 1)]
                    a = A[kij]; a[0] += sw_[n_]; a[1] += sk[n_]; a[2] += sv[n_]; a[3] += h[n_]
            print(f"{stratum}/{sd.name}: {time.time() - t0:.0f} s", flush=True)
    geod = Geod(ellps="WGS84"); rx = sw.receivers()
    kt = pd.read_csv(here / "results-data/near_limits/ims_tl_kraken.csv", dtype={"quantile": str})
    rd = pd.read_csv(here / "results-data/near_limits/ims_ram_delta.csv")
    req = json.loads((here / "data/ocean_paths/request_ims.json").read_text())
    qlat = {p["name"].split("-")[0][3:]: p["a"][1] for p in req["paths"]}; xs = np.array([qlat[q] for q in QS])
    order = np.argsort(xs)
    tlq = {}
    for stn in ("H01W", "H08S"):
        g = kt[(kt.station == stn) & np.isclose(kt.src_depth_m, ZS)]; dd = rd[(rd.path == f"imp500_{stn}") & np.isclose(rd.src_depth_m, ZS)].set_index("fc_hz").delta_db
        tlq[stn] = {fc: g[g.fc_hz == fc].set_index("quantile").tl_db[QS].values - float(np.interp(np.log10(fc), np.log10(dd.index.values), dd.values)) for fc in BANDS}
    blk = {r["station"]: f'{r["blockage"]} ({r["blockage_by_quantile"]})' for r in csv.DictReader(open(here / "data/kadri_package/windows.csv"))}
    R = json.loads((here / "results-data/f35a_cal/eta_cal_summary.json").read_text())
    R = (R.get("peak_ratio", R))["T_C2"]["R_per_s"] if "T_C2" in R.get("peak_ratio", R) else 3.0129
    Sb = {fc: float(np.ravel(B.band_fraction(fc, np.array([1.0 / TAU]), 2))[0]) for fc in BANDS}
    hms = lambda s: time.strftime("%H:%M:%S", time.gmtime(T0 + s))
    rows = []
    for name, key in OPTIONS:
        A = acc[key]; ks = sorted(A, key=lambda k: -A[k][0]); W = np.array([A[k][0] for k in ks]); tot = W.sum()
        keep = ks[: int(np.searchsorted(np.cumsum(W) / tot, 0.99)) + 1]
        lat_c = np.array([(k[0] + 0.5) * BIN for k in keep]); lon_c = np.array([(k[1] + 0.5) * BIN for k in keep])
        depth = AG.depth_at(lat_c, lon_c)
        for i, k in enumerate(keep):
            w, wk, wv, h = A[k]; cdf = np.cumsum(h) / h.sum()
            tq = [TB[min(int(np.searchsorted(cdf, q)), len(TB) - 2) + 1] for q in (0.05, 0.5, 0.95)]
            base = dict(option=name, option_code=key, bin_lat=lat_c[i], bin_lon=lon_c[i], weight=w / tot, seafloor_depth_m=round(float(depth[i]), 0),
                        impact_utc_q05=hms(tq[0]), impact_utc_q50=hms(tq[1]), impact_utc_q95=hms(tq[2]),
                        kinetic_energy_j=wk / w, vertical_kinetic_energy_j=wv / w)
            for stn in STATIONS:
                sla, slo = rx[stn]; baz, _, d = geod.inv(slo, sla, lon_c[i], lat_c[i]); d /= 1000.0
                r = dict(base, station=stn, range_km=round(d, 1), backazimuth_deg=round(baz % 360, 2),
                         arrival_utc_start=hms(tq[0] + d / (1.482 + 0.012)), arrival_utc_end=hms(tq[2] + d / (1.482 - 0.012)),
                         blockage=blk.get(stn, ""), tl_sd_db=TL_SD)
                if stn in tlq:
                    tl = {fc: float(np.interp(np.clip(lat_c[i], xs.min(), xs.max()), xs[order], tlq[stn][fc][order])) for fc in BANDS}
                    gain = sum(Sb[fc] * 10 ** (-tl[fc] / 10) for fc in BANDS)
                    for fc in BANDS:
                        r[f"tl_db_{fc:g}hz"] = round(tl[fc], 1)
                    for e in ETAS:
                        se = e * (wk / w) * B.RHO_C / (2 * np.pi) * gain
                        r[f"exposure_pa2s_eta{e:g}"] = se; r[f"peak_pa_eta{e:g}"] = float(np.sqrt(R * se))
                rows.append(r)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(out / "predictions.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields); wr.writeheader(); wr.writerows(rows)
    json.dump(dict(script="prepare/kadri_predictions.py", eof_module_sha256=hashlib.sha256(open(eofmod, "rb").read()).hexdigest(),
                   exchange=exch, p_family=PF, options=OPTIONS, R_per_s=R, tau_s=TAU, src_depth_m=ZS, tl_sd_db=TL_SD, etas=ETAS,
                   n_rows=len(rows), labels=["core (b) split-half NOT converged", "two-tank bookkeeping only", "P(family) held fixed",
                                             "uncorrected fuel", "provisional sampler", "PROVISIONAL", "DRAFT for Pete's review"]),
              open(out / "predictions_meta.json", "w"), indent=1)
    print(len(rows), {n: sum(1 for r in rows if r["option"] == n and r["station"] == "H01W") for n, _ in OPTIONS})


if __name__ == "__main__":
    main(*sys.argv[1:5])
