"""windows_core_b.csv for the Kadri package (DRAFT for Pete's review; NOTHING is sent). Replaces the stand-in
windows.csv as the package's primary windows table; the stand-in file is kept unchanged.
Per receiver x 00:19 option (options 1-3; Holland H1/H2 not yet estimable - targeted sampler in progress):
  - arrival quantiles and window: results-data/search_windows/next-run-b-v2/mixture_reweighted/core_set
    (core (b), +unpowered intended, families re-weighted by Z_00:19; SOFAR branch); the request window is the
    union over options 1-3 (core_recommended_windows.csv).
  - back-azimuth and range quantiles: weighted over the impact bins of results-data/kadri_package/next-run-b/
    predictions.csv (core (b), +alive, fixed P(family): DECLARED mismatch, positions move < 0.1 deg between the two).
  - blockage: IMS from predictions.csv row flags (weight share by class); IMOS from the stand-in windows.csv flags
    (shared ocean transport, stand-in positions; DECLARED).
Labels carried: core (b) split-half NOT converged; provisional on TL calibration (architecture, 17:50 -0600).
Usage: python build_windows_coreb.py"""
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod

H = Path(__file__).resolve().parents[2]
G = Geod(ellps="WGS84")


def wq(x, w, qs):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return [float(np.interp(q, c, x[o])) for q in qs]


def main():
    cs = H / "results-data/search_windows/next-run-b-v2/mixture_reweighted/core_set"
    byo = pd.read_csv(cs / "core_windows_by_option.csv")
    rec = pd.read_csv(cs / "core_recommended_windows.csv")
    pr = pd.read_csv(H / "results-data/kadri_package/next-run-b/predictions.csv")
    old = pd.read_csv(H / "data/kadri_package/windows.csv").set_index("station")
    rows = []
    for _, r in byo[(byo.variant == "unpowered") & (byo.branch == "sofar") & (byo.option_no <= 3)].iterrows():
        st = str(r.receiver)
        p = pr[pr.option == r.option]
        if st in ("H01W", "H08S", "H08N"):
            s = p[p.station == st]
            w = s.weight.values
            az, rng = np.mod(s.backazimuth_deg.values, 360), s.range_km.values
            cls = s.blockage.str.split(" ").str[0]
            blk = ";".join(f"{k}:{w[cls.values == k].sum() / w.sum():.3f}" for k in ["open", "partial", "blocked"])
            worst = "blocked" if (w[cls.values == "blocked"].sum() / w.sum()) > 0.5 else "partial" if (cls != "open").any() else "open"
            src = "core (b) bins"
        else:
            s = p[p.station == "H01W"].drop_duplicates(["bin_lat", "bin_lon"])
            w = s.weight.values
            la, lo = old.loc[st, "lat"], old.loc[st, "lon"]
            a, _, d = G.inv(np.full(len(s), lo), np.full(len(s), la), s.bin_lon.values, s.bin_lat.values)
            az, rng = np.mod(a, 360), d / 1e3
            worst, blk, src = old.loc[st, "blockage"], "stand-in: " + old.loc[st, "blockage_by_quantile"], "stand-in flag"
        rw = rec[(rec.variant == "unpowered") & (rec.branch == "sofar") & (rec.receiver.astype(str) == st)].iloc[0]
        b, g = wq(az, w, [0.025, 0.5, 0.975]), wq(rng, w, [0.025, 0.5, 0.975])
        rows.append(dict(station=st, option=r.option, ess_pooled=int(r.ess_pooled), arrival_q2p5=r["q2.5"], arrival_median=r.q50,
                         arrival_q97p5=r["q97.5"], option_window=f"{r.window_start}-{r.window_end}",
                         request_window_utc=f"2014-03-08 {rw.window_start}-{rw.window_end}",
                         backazimuth_q2p5=round(b[0], 2), backazimuth_median=round(b[1], 2), backazimuth_q97p5=round(b[2], 2),
                         range_km_q2p5=round(g[0], 1), range_km_median=round(g[1], 1), range_km_q97p5=round(g[2], 1),
                         blockage=worst, blockage_share=blk, blockage_source=src, converged=r.converged,
                         status="DRAFT; core (b) unconverged; +unpowered; families re-weighted; SOFAR branch; provisional on TL calibration"))
    for st in sorted(set(byo.receiver.astype(str))):
        rows.append(dict(station=st, option="00:19 Holland H1 / H2", status="not yet estimable - targeted sampler in progress (ESS < 1,000)"))
    out = H / "data/kadri_package/windows_core_b.csv"
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    print(df[df.ess_pooled.notna()][["station", "option", "arrival_median", "request_window_utc", "backazimuth_median", "range_km_median", "blockage"]].to_string(index=False))


if __name__ == "__main__":
    main()
