"""windows.csv for the Kadri package (DRAFT for Pete's review; brief section 9). Per station: predicted
SOFAR arrival quantiles (true UTC) from the parametric 7th-arc STAND-IN (rerun on end of flight's impacts
when published), the window [q0.5 - 120 s, q99.5 + 120 s], back-azimuth and range quantiles, and a
blockage flag from the shared ocean transport paths (ruling H5) at the stand-in's five latitude
quantiles, by a DECLARED rule applied before the final 100 km (receiver slope):
  blocked: land, or track shallower than 200 m for >= 10 km;  partial: minimum track depth < 2,000 m
  (sound-channel interaction plausible);  open: otherwise. The flag reported is the worst over quantiles,
  with the count of quantiles in each class.
Model: impact time 00:19:37 + N(300, 180) s; c_g ~ N(1.482, 0.006) km/s (as prepare/imos_preregistration).
Usage: python build_windows.py <paths_export_dir> <stand-in summary json> <out.csv>"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod
sys.path.insert(0, str(Path(__file__).parents[1]))
import imos_preregistration as P  # noqa: E402

G = Geod(ellps="WGS84")


def blockage(exp, station):
    cls = []
    for q in ["025", "250", "500", "750", "975"]:
        f = Path(exp) / f"imp{q}-{station}_bathymetry.csv"
        d = pd.read_csv(f)
        far = d[d.s_m < d.s_m.max() - 100e3]
        sh, run, best = (far.depth_m < 200).values, 0, 0
        for v in sh:
            run = run + 1 if v else 0
            best = max(best, run)
        if (far.depth_m <= 0).any() or best * 0.25 >= 10:
            cls.append("blocked")
        elif far.depth_m.min() < 2000:
            cls.append("partial")
        else:
            cls.append("open")
    worst = "blocked" if "blocked" in cls else "partial" if "partial" in cls else "open"
    return worst, ";".join(f"{k}:{cls.count(k)}" for k in ["open", "partial", "blocked"])


def main(exp, summary, out):
    st = pd.read_csv(Path(__file__).parents[2] / "data/stations.csv", comment="#")
    ims = st[st.triad.isin(["H01W", "H08S", "H08N"])].groupby("triad").agg(lat=("latitude_deg", "mean"), lon=("longitude_deg", "mean"), depth=("hydrophone_depth_m", "mean"))
    meta = P.parse_meta()
    sta = {k: (r.lat, r.lon, r.depth, "IMS triad centroid") for k, r in ims.iterrows()}
    for cid, dep in [("3315", 447), ("3376", 409), ("3250", 221), ("3274", 151), ("3275", 164)]:
        sta[cid] = (meta[cid]["lat"], meta[cid]["lon"], dep, "IMOS logger (single hydrophone, duty-cycled)")
    rng = np.random.default_rng(P.sct.SEED)
    ridge, grid, dens, _ = P.sct.ridge_and_marginal(summary)
    q, _ = P.sct.fit_small_circle(ridge)
    pr = P.sct.draw_prior(rng, q, grid, dens, P.sct.N_PRIOR, P.sct.BASE["sigma_x_nm"])
    n = len(pr)
    t_imp = P.sct.BASE["mu_t_s"] + rng.normal(0, P.sct.BASE["sigma_t_s"], n)
    c = rng.normal(P.C_G, P.SD_C, n)
    rows = []
    for name, (la, lo, dep, kind) in sta.items():
        az, _, d = G.inv(np.full(n, lo), np.full(n, la), pr[:, 1], pr[:, 0])
        ta = t_imp + d / 1000 / c
        qs = np.quantile(ta, [0.005, 0.025, 0.5, 0.975, 0.995])
        ts = lambda s: str((P.T_IMPACT_REF + pd.Timedelta(seconds=float(s))).tz_convert(None))[:19]  # noqa: E731
        flag, counts = blockage(exp, name)
        rows.append(dict(station=name, kind=kind, lat=round(la, 6), lon=round(lo, 6), receiver_depth_m=round(dep),
                         arrival_q2p5=ts(qs[1]), arrival_median=ts(qs[2]), arrival_q97p5=ts(qs[3]),
                         window_start=ts(qs[0] - 120), window_end=ts(qs[4] + 120),
                         backazimuth_q2p5=round(float(np.quantile(np.mod(az, 360), 0.025)), 2),
                         backazimuth_median=round(float(np.quantile(np.mod(az, 360), 0.5)), 2),
                         backazimuth_q97p5=round(float(np.quantile(np.mod(az, 360), 0.975)), 2),
                         range_km_q2p5=round(float(np.quantile(d, 0.025)) / 1000, 1), range_km_median=round(float(np.median(d)) / 1000, 1),
                         range_km_q97p5=round(float(np.quantile(d, 0.975)) / 1000, 1), blockage=flag, blockage_by_quantile=counts,
                         status="DRAFT; stand-in impact PDF; SOFAR branch only"))
    pd.DataFrame(rows).to_csv(out, index=False)
    print(pd.DataFrame(rows)[["station", "arrival_median", "window_start", "window_end", "backazimuth_median", "range_km_median", "blockage", "blockage_by_quantile"]].to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
