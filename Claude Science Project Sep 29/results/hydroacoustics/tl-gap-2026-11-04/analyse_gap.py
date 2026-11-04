"""Analysis for the Cape Leeuwin / Wake loss gap (4 Nov 2026). Reproduces the key numbers of README.md from:
  --runs   assembled diagnostic runs (assemble_gap.py outputs: band_tl_runs.csv, range_curves.csv.gz; swap and fix band tables)
  --p3     Phase 3 table tl_used_atlantic_pacific.csv (frozen Wake paths, 13 frequencies per band)
  --p4     Phase 4 table tl-table-hard-seabed-known-source-paths.csv
  --dense  dense arc grid tl_dense_bands.csv (3 Nov 2026)
  --resid  held-out residual table v2_level-residual-table.csv (3 Nov 2026)
  --ridge  f35a-raw-ridge folder (f35a-raw-measurements.csv, f35a-raw-band-exposure.csv)
Usage: python analyse_gap.py <runs_dir> <fix_band_csv> <swap_band_csv> <p3_csv> <p4_csv> <dense_csv> <resid_csv> <ridge_dir>"""
import sys
import numpy as np, pandas as pd

B10 = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; B12 = B10 + [50.0, 63.0]
TAU = 3.2976933272535214; RHO_C = 1025 * 1500.0; W63 = (64.0 - 63.0 / 2 ** (1 / 6)) / (63.0 * 2 ** (1 / 6) - 63.0 / 2 ** (1 / 6))
NOISE, T_WIN, E10, EF = 103.68, 30.0, 10e9, 0.9e9
SE_W = {"H11N": 113.87, "H11S": 109.03}      # 5-40 Hz band exposure, mean over elements, dB re 1 uPa^2 s (recomputed below)
R_W = {"H11N": 3248.798, "H11S": 3341.5}


def band_fraction(fc, f_r, slope):           # copy of imos_stageB_map.band_fraction (flat to f_r, f^-slope, over 1-500 Hz)
    f = np.logspace(0, np.log10(500), 4000); esd = np.where(f <= f_r, 1.0, (f / f_r) ** (-slope)); tot = np.trapezoid(esd, f)
    lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6); m = (f >= lo) & (f <= hi)
    return np.trapezoid(esd[m], f[m]) / tot


S10 = np.array([band_fraction(fc, 1 / TAU, 2) for fc in B10])
S12 = np.array([band_fraction(fc, 1 / TAU, 2) for fc in B12]) * np.array([1] * 11 + [W63])
G = lambda tl, S=S10: RHO_C / (2 * np.pi) * np.nansum(S * 10 ** (-np.asarray(tl, float) / 10))   # noqa: E731
TLeff = lambda tl, S=S10: -10 * np.log10(G(tl, S) / (RHO_C / (2 * np.pi)) / S.sum())            # noqa: E731


def main(runs, fixcsv, swapcsv, p3csv, p4csv, densecsv, residcsv, ridge):
    Bt = pd.read_csv(f"{runs}/band_tl_runs.csv"); PAC = pd.read_csv(p3csv); h = pd.read_csv(p4csv)
    td = pd.read_csv(densecsv); v2 = pd.read_csv(residcsv); FX = pd.read_csv(fixcsv); Bs = pd.read_csv(swapcsv)
    M = pd.read_csv(f"{ridge}/f35a-raw-measurements.csv").set_index("element"); BD = pd.read_csv(f"{ridge}/f35a-raw-band-exposure.csv")
    SE5 = M.exposure_4_64_Pa2s_raw.to_dict()
    SE40 = {el: float(g[g.fc_hz.between(5, 40)].excess_pa2s.clip(lower=0).sum()) for el, g in BD.groupby("element")}
    for t in SE_W:
        SE_W[t] = 10 * np.log10(np.mean([SE40[e] for e in SE40 if e.startswith(t)]) / 1e-12)
    print("SE 5-40 dB:", {k: round(v, 2) for k, v in SE_W.items()})
    p3 = lambda n, z, sb="L1", b=B12: PAC[(PAC.name == n) & np.isclose(PAC.src_depth_m, z) & (PAC.seabed_variant == sb)].set_index("fc_hz").tl_db.reindex(b).values  # noqa: E731
    # 1. coupling re-inversion (geometric mean of triads; triad = mean element exposure)
    for z in (2, 10, 30):
        for score in ("5-63", "5-40"):
            e = []
            for t in ("H11N", "H11S"):
                els = [x for x in SE5 if x.startswith(t)]
                if score == "5-63":
                    e.append(np.mean([SE5[x] for x in els]) / (EF * G(p3(f"f35a-{t}", z), S12)))
                else:
                    e.append(np.mean([SE40[x] for x in els]) / (EF * G(p3(f"f35a-{t}", z, b=B10))))
            print(f"eta frozen L1 {z} m scored {score}: {np.exp(np.mean(np.log(e))):.4g}")
    # 2. gap with one convention (dense arc grid vs Wake rerun at 7 frequencies)
    rv = Bt[(Bt.kind == "rev") & (Bt.seabed == "L1")]
    wk = lambda t, z: rv[(rv.path == f"f35a-{t}") & np.isclose(rv.src_depth_m, z)].set_index("fc_hz").tl_db.reindex(B10).values  # noqa: E731
    cl = td[td.station == "H01W"]; rows = []
    for (p, lat), g in cl.groupby(["path", "src_lat"]):
        for z in (2, 10, 30):
            ta = g[np.isclose(g.src_depth_m, z)].set_index("fc_hz").tl_db.reindex(B10).values
            snr = np.mean([SE_W[t] + 10 * np.log10(E10 / EF) + 10 * np.log10(G(ta) / G(wk(t, z))) - 10 * np.log10(T_WIN) - NOISE for t in SE_W])
            naive = np.mean([SE_W[t] + 10 * np.log10(E10 / EF) + 10 * np.log10(R_W[t] / g.range_km.iloc[0]) - 10 * np.log10(T_WIN) - NOISE for t in SE_W])
            rows.append(dict(lat=lat, z=z, snr_frozen=snr, naive=naive))
    A = pd.DataFrame(rows); a10 = A[A.z == 10]
    print("frozen SNR median", round(a10.snr_frozen.median(), 2), "equal-loss", round(a10.naive.median(), 2),
          "gap median", round((a10.naive - a10.snr_frozen).median(), 2))
    # 3. swap test
    for sw, b0 in (("SW_wake_warm", "f35a-H11N"), ("SW_arc_cold", "arc35.5S-H01W"), ("SW_arc39_cold", "arc39.0S-H01W")):
        t1 = TLeff(Bs[(Bs.path == sw) & (Bs.kind == "fwd")].set_index("fc_hz").tl_db.reindex(B10).values)
        t0 = TLeff(Bt[(Bt.path == b0) & (Bt.kind == "fwd") & (Bt.seabed == "L1")].set_index("fc_hz").tl_db.reindex(B10).values)
        print(f"swap {sw}: {t1 - t0:+.2f} dB")
    # 4. corrected prediction (bias N(7,3); other sd 4.03; anchor 2.81 dB; depth 2/10/30 m)
    rng = np.random.default_rng(20261104); N = 20000; out = []
    for lat, g in A.groupby("lat"):
        zz = rng.choice([2, 10, 30], N); base = g.set_index("z").snr_frozen.reindex(zz).values
        x = base + rng.normal(7.0, 3.0, N) + rng.normal(0, np.sqrt(3 ** 2 + 2.5 ** 2 + 1), N) + rng.normal(0, 0.647 * 10 / np.log(10), N)
        out.append(dict(lat=lat, med=np.median(x), p05=np.percentile(x, 5), p95=np.percentile(x, 95), P5=np.mean(x > 5)))
    C = pd.DataFrame(out)
    print("corrected median over arc", round(C.med.median(), 2), "p05/p95 at median", round(C.p05.median(), 2), round(C.p95.median(), 2),
          "P(>5 dB) median", round(C.P5.median(), 3))


if __name__ == "__main__":
    main(*sys.argv[1:9])
