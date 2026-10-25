"""F-35A (9 Apr 2019) raw Wake Island IMS records: measurements, 20 Hz gap test, implied source spectrum and the coupling
ridge eta_rad(z_eff, S) through the module chain. Follows the pre-registration f35a-raw-prereg.md (artifact 493a290e).
Inputs: data/*.mseed + data/H11_resp_2019-04-09.xml (fetch_raw.py), out/tl/tl_ridge.csv (tl_ridge.py),
module branch hypothesis/hydroacoustics (read only) at ./H, optional out/ram_ridge.csv (ram_ridge.py).
Outputs: out/*.csv, out/analysis.pkl. Units: Pa, Pa^2 s, dB re 1 uPa, dB re 1 uPa^2/Hz, Pa^2 s/Hz; J.
Usage (from t1/): python scripts/f35a_raw_analysis.py"""
import sys, pathlib, pickle, json
import numpy as np, pandas as pd, obspy
from scipy import signal
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "H/prepare")); sys.path.insert(0, str(ROOT / "H/prepare/metz_f35a"))
import raw_lib as RL                       # noqa: E402
from imos_stageB_map import band_fraction  # noqa: E402  (module source-spectrum band fractions, unchanged)
import prereg as PR                        # noqa: E402  (module constants: RHO_C, BANDS, W63, TAU_FALLBACK)
OUT = ROOT / "out"; DATA = ROOT / "data"
DEPTHS = [1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
EJ = {"low": 700e6, "mid": 900e6, "high": 1100e6}
rng = np.random.default_rng(20261025)

# ---------------- P1-P2 data and response
inv = obspy.read_inventory(str(DATA / "H11_resp_2019-04-09.xml"))
coords = {sta.code: (sta[0].latitude, sta[0].longitude, -sta[0].elevation) for net in inv for sta in net}
P = {el: RL.to_pa(obspy.read(str(DATA / f"{el}_event.mseed"))[0], inv) for el in RL.ELS}
BG = {}
for el in RL.ELS:
    for h in ("01", "04", "07", "14", "17", "20", "23"):
        s = obspy.read(str(DATA / f"{el}_bg{h}.mseed")); s.merge(fill_value=None)
        for tr in s.split():
            if tr.stats.npts >= 250 * 120:
                BG.setdefault(el, []).append(RL.to_pa(tr, inv))

# ---------------- P3-P5, P9 envelope operator, times, instantaneous peaks
OBS = {}
for el, tr in P.items():
    x = RL.bp(tr.data, 4.0, 64.0); tc, ms = RL.ms_1s(x); tabs = (tr.stats.starttime - RL.DAY) + tc; L = 10 * np.log10(ms / 1e-12)
    fr = RL.FRAME[el[:4]]; m = (tabs >= fr[0] - RL.DAY) & (tabs <= fr[1] - RL.DAY)
    o = RL.obs_operator(tabs[m], L[m], RL.HOP)
    ns = (tabs >= RL.NOISE_SEG[0] - RL.DAY) & (tabs <= RL.NOISE_SEG[1] - RL.DAY)
    o2 = RL.obs_operator(tabs[m], L[m], RL.HOP, noise_db=10 * np.log10(np.mean(ms[ns]) / 1e-12))
    o.update({f"N2_{k}": v for k, v in o2.items() if k in ("noise_db", "snr_db", "se_pa2s", "span_5_95_s", "w6_s")})
    ts = tr.stats.starttime - RL.DAY; i0 = int((o["peak_t"] - 15 - ts) * RL.FS); i1 = int((o["peak_t"] + 15 - ts) * RL.FS)
    for lab, (lo, hi) in {"2_100": (2, 100), "4_64": (4, 64), "4_40": (4, 40)}.items():
        o[f"ipk_{lab}_pa"] = float(np.max(np.abs(RL.bp(tr.data, lo, hi)[i0:i1])))
    o["ipk_resp_only_pa"] = float(np.max(np.abs(tr.data[i0:i1])))
    o["env_t"], o["env_L"] = tabs[m], L[m]
    OBS[el] = o

# ---------------- P6 back-azimuth
srcW, srcP = (40.64, 142.96), (40.4496, 142.9237)
pairs = [(0, 1), (1, 2), (2, 0)]; BAZ = []; GEO = {}
for tri in ("H11N", "H11S"):
    els = [tri + str(i) for i in (1, 2, 3)]
    lat0 = np.mean([coords[e][0] for e in els]); lon0 = np.mean([coords[e][1] for e in els])
    xy = RL.enu([coords[e][0] for e in els], [coords[e][1] for e in els], lat0, lon0)
    GEO[tri] = {k: RL.G.inv(lon0, lat0, s[1], s[0])[0] % 360 for k, s in (("W", srcW), ("P", srcP))}
    for band in ((4, 64), (5, 40)):
        X = [RL.bp(P[e].data, *band) for e in els]; ts = P[els[0]].stats.starttime - RL.DAY
        a = min(OBS[e]["arr_start"] for e in els) - 3; b = max(OBS[e]["arr_end"] for e in els) + 3
        for w0 in np.arange(a, b - 6 + 1e-6, 1.0):
            i0 = int((w0 - ts) * RL.FS); i1 = i0 + int(6 * RL.FS)
            seg = [x[i0:i1] * signal.windows.tukey(i1 - i0, 0.1) for x in X]
            dc = [RL.xcorr_delay(seg[i], seg[j], maxlag=int(2.5 * RL.FS)) for i, j in pairs]
            d = [q[0] for q in dc]; baz, v, s = RL.plane_wave(xy, d, pairs)
            BAZ.append(dict(triad=tri, band=f"{band[0]}-{band[1]}", t_mid=w0 + 3, baz_deg=baz, v_app_m_s=v, closure_ms=abs(sum(d)) * 1e3,
                            cc_min=min(q[1] for q in dc), energy=np.mean([np.sum(q ** 2) for q in seg]) / RL.FS))
B = pd.DataFrame(BAZ)
def baz_summary(g):
    h = g[(g.closure_ms <= 16) & g.v_app_m_s.between(1430, 1530)]; w = h.energy.values; ang = np.radians(h.baz_deg.values)
    m = np.degrees(np.arctan2(np.sum(w * np.sin(ang)), np.sum(w * np.cos(ang)))) % 360; dev = ((h.baz_deg.values - m + 180) % 360) - 180
    vm = np.sum(w * h.v_app_m_s) / np.sum(w)
    return pd.Series(dict(n_windows=len(g), n_pass_gates=len(h), baz_wmean_deg=m, baz_wsd_deg=np.sqrt(np.sum(w * dev ** 2) / np.sum(w)),
                          v_app_wmean_m_s=vm, v_app_wsd_m_s=np.sqrt(np.sum(w * (h.v_app_m_s - vm) ** 2) / np.sum(w)), closure_median_ms=h.closure_ms.median()))
BS = B.groupby(["triad", "band"]).apply(baz_summary).reset_index()
BS["geodesic_baz_from_W_deg"] = BS.triad.map(lambda t: GEO[t]["W"]); BS["geodesic_baz_from_P_deg"] = BS.triad.map(lambda t: GEO[t]["P"])
BS["metz_digitised_baz_deg"] = BS.triad.map({"H11N": 320.610004, "H11S": 321.729193})
BS["metz_digitised_v_app_m_s"] = BS.triad.map({"H11N": 1473.019635, "H11S": 1463.152936})

# ---------------- P7 band exposures
def band_edges(fc): return fc / 2 ** (1 / 6), min(fc * 2 ** (1 / 6), 118.0)
BR = []
for el in RL.ELS:
    tr = P[el]; ts = tr.stats.starttime - RL.DAY; o = OBS[el]; wa = o["arr_start"] - 2; wb = o["arr_end"] + 2; Wl = wb - wa
    i0 = int((wa - ts) * RL.FS); i1 = int((wb - ts) * RL.FS)
    n0 = int((RL.NOISE_SEG[0] - RL.DAY - ts) * RL.FS); n1 = int((RL.NOISE_SEG[1] - RL.DAY - ts) * RL.FS)
    for fc in RL.BANDS:
        lo, hi = band_edges(fc); x = RL.bp(tr.data, lo, hi); ew = float(np.sum(x[i0:i1] ** 2) / RL.FS)
        ns = x[n0:n1]; k = len(ns) // 250; ms1 = (ns[:k * 250] ** 2).reshape(k, 250).mean(1); Nb = float(ms1.mean()); Nbm = float(np.median(ms1))
        Lw = int(Wl * RL.FS); smp_all = []; smp_pre = []
        for j, sg in enumerate([ns] + [RL.bp(b.data, lo, hi)[2500:-2500] for b in BG[el]]):
            for q in range(len(sg) // Lw):
                v = np.sum(sg[q * Lw:(q + 1) * Lw] ** 2) / RL.FS - Nb * Wl; smp_all.append(v)
                if j == 0: smp_pre.append(v)
        BR.append(dict(element=el, triad=el[:4], fc_hz=fc, f_lo=lo, f_hi=hi, bw_hz=hi - lo, win_start_utc_s=wa, win_s=Wl, E_window_pa2s=ew,
                       noise_ms_mean_pa2=Nb, noise_ms_median_pa2=Nbm, excess_pa2s=ew - Nb * Wl, excess_mediannoise_pa2s=ew - Nbm * Wl,
                       sigma_pa2s=float(np.std(smp_all)), n_sigma_windows=len(smp_all), sigma_pre_only_pa2s=float(np.std(smp_pre)), n_pre_windows=len(smp_pre),
                       ratio_db=10 * np.log10(ew / (Nb * Wl))))
BD = pd.DataFrame(BR)
BD["measured"] = (BD.excess_pa2s >= 2 * BD.sigma_pa2s) & (BD.ratio_db >= 3)
BD["measured_pre_sigma"] = (BD.excess_pa2s >= 2 * BD.sigma_pre_only_pa2s) & (BD.ratio_db >= 3)   # deviation variant (not pre-registered)

# ---------------- P8 spectra and G1-G4 gap tests
def dband(f, S, c, lo1, hi1, lo2, hi2):
    dB = lambda m: 10 * np.log10(np.maximum(np.mean(S[..., m], axis=-1), 1e-30))
    return dB((f >= c[0]) & (f <= c[1])) - 0.5 * (dB((f >= lo1) & (f <= hi1)) + dB((f >= lo2) & (f <= hi2)))
GAPDEF = {"D20": ((18, 24), 12, 17, 26, 34), "D60": ((55, 65), 45, 52, 68, 80)}
SPEC = {}; GR = []
for el in RL.ELS:
    tr = P[el]; ts = tr.stats.starttime - RL.DAY; o = OBS[el]; wa = o["arr_start"] - 2; wb = o["arr_end"] + 2; Wl = wb - wa
    i0 = int((wa - ts) * RL.FS); i1 = int((wb - ts) * RL.FS); n0 = int((RL.NOISE_SEG[0] - RL.DAY - ts) * RL.FS); n1 = int((RL.NOISE_SEG[1] - RL.DAY - ts) * RL.FS)
    f, Pa = RL.welch_psd(tr.data[i0:i1]); f, Pn = RL.welch_psd(tr.data[n0:n1]); f, Seg = RL.welch_segments(tr.data[i0:i1])
    ch = np.array([RL.welch_psd(b.data[2500:-2500][k * 15000:(k + 1) * 15000])[1] for b in BG[el] for k in range((len(b.data) - 5000) // 15000)])
    pct = np.percentile(ch, [5, 50, 95], axis=0)
    SPEC[el] = dict(f=f, Pa=Pa, Pn=Pn, esd=(Pa - Pn) * Wl, Wlen=Wl, bg5=pct[0], bg50=pct[1], bg95=pct[2])
    for k, (c, l1, h1, l2, h2) in GAPDEF.items():
        Dx = dband(f, np.maximum(Pa - Pn, 1e-30), c, l1, h1, l2, h2)
        bs = [dband(f, np.maximum(Seg[rng.integers(0, len(Seg), len(Seg))].mean(0) - Pn, 1e-30), c, l1, h1, l2, h2) for _ in range(2000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        GR.append(dict(element=el, statistic=k, gap_depth_excess_db=Dx, ci95_lo_db=lo, ci95_hi_db=hi,
                       verdict="present" if (Dx <= -3 and hi < 0) else ("absent" if lo > -3 else "unresolved"),
                       gap_depth_arrival_psd_db=dband(f, Pa, c, l1, h1, l2, h2), gap_depth_noise_pre_db=dband(f, Pn, c, l1, h1, l2, h2),
                       gap_depth_noise_bg_median_db=dband(f, pct[1], c, l1, h1, l2, h2), n_welch_segments=len(Seg)))
GD = pd.DataFrame(GR)
resp = inv.select(station="H11N1")[0][0][0].response
fr_ = np.linspace(10, 40, 301); G2 = float(dband(fr_, np.abs(resp.get_evalresp_response_for_frequencies(fr_, output="DEF")) ** 2, (18, 24), 12, 17, 26, 34))

# ---------------- R1-R2 TL vectors
T = pd.read_csv(OUT / "tl/tl_ridge.csv")
rk = pd.read_csv(ROOT / "H/results-data/ram_check/ram_vs_kraken.csv"); rk = rk[rk.path == "f35a_H11S"]
RAMNEW = pd.read_csv(OUT / "ram_ridge.csv") if (OUT / "ram_ridge.csv").exists() else None
def _delta(tab, z, bands, col_r="tl_ram_db", col_k="tl_kraken_db"):
    g = tab[np.isclose(tab.src_depth_m, z)].sort_values("fc_hz"); c = (g[col_r] - g[col_k]).values; f = g.fc_hz.values
    return np.interp(np.log(bands), np.log(f), c, left=c[0], right=c[-1])
def ram_delta(zs, bands, triad="H11S", source="module"):
    if source == "module":
        tab = rk
        if zs <= 10: return _delta(tab, 10.0, bands)
        if zs >= 30: return _delta(tab, 30.0, bands)
        return 0.5 * (_delta(tab, 10.0, bands) + _delta(tab, 30.0, bands))
    tab = RAMNEW[RAMNEW.path == f"W-{triad}"]; zz = sorted(tab.src_depth_m.unique())
    return _delta(tab, min(zz, key=lambda z: abs(z - max(zs, zz[0]))) if zs not in zz else zs, bands)
def tlv(path, zs, chain, bands, ram_source="module"):
    g = T[(T.path == path) & np.isclose(T.src_depth_m, zs)].set_index("fc_hz").reindex(bands).tl_db.values.astype(float)
    return g + (ram_delta(zs, bands, path[-4:], ram_source) if chain == "KRAKEN_RAM" else 0.0)

# ---------------- R3 implied source spectrum, slopes, cavity, corner
SS = []
for r in BD.itertuples():
    for zs in DEPTHS:
        for chn in ("KRAKEN_ONLY", "KRAKEN_RAM"):
            tl = tlv("W-" + r.triad, zs, chn, [r.fc_hz])[0]; rx = 10 * np.log10(max(r.excess_pa2s, 1e-30) / 1e-12 / r.bw_hz)
            SS.append(dict(element=r.element, triad=r.triad, fc_hz=r.fc_hz, src_depth_m=zs, chain=chn, measured=r.measured, rx_esd_db=rx, tl_db=tl, src_esd_db=rx + tl))
SS = pd.DataFrame(SS)
def ols(x, y):
    A = np.vstack([np.ones_like(x), x]).T; c, *_ = np.linalg.lstsq(A, y, rcond=None); res = y - A @ c
    return c, float(np.sqrt(np.sum(res ** 2) / max(len(y) - 2, 1) * np.linalg.inv(A.T @ A)[1, 1]))
SL = []
for (chn, zs), g in SS.groupby(["chain", "src_depth_m"]):
    for lab, (lo, hi) in {"5-40": (5, 40), "5-63": (5, 63), "5-16": (5, 16)}.items():
        h = g[g.measured & g.fc_hz.between(lo, hi)]
        pb = h.groupby("fc_hz").agg(S=("src_esd_db", "mean"), R=("rx_esd_db", "mean"), n=("element", "count")); pb = pb[pb.n >= 2]
        c, se = ols(np.log2(pb.index.values), pb.S.values); cr, ser = ols(np.log2(pb.index.values), pb.R.values)
        SL.append(dict(chain=chn, src_depth_m=zs, band=lab, who="pooled", n_bands=len(pb), src_esd_slope_db_oct=c[1], se=se, rx_esd_slope_db_oct=cr[1], rx_se=ser,
                       bands=" ".join(f"{v:g}" for v in pb.index)))
        for el, ge in h.groupby("element"):
            if len(ge) >= 3:
                c, se = ols(np.log2(ge.fc_hz.values), ge.src_esd_db.values); cr, ser = ols(np.log2(ge.fc_hz.values), ge.rx_esd_db.values)
                SL.append(dict(chain=chn, src_depth_m=zs, band=lab, who=el, n_bands=len(ge), src_esd_slope_db_oct=c[1], se=se, rx_esd_slope_db_oct=cr[1], rx_se=ser,
                               bands=" ".join(f"{v:g}" for v in ge.fc_hz)))
SLd = pd.DataFrame(SL)
CAV = []
for (chn, zs), g in SS.groupby(["chain", "src_depth_m"]):
    h = g[g.measured & g.fc_hz.between(5, 63)]; pb = h.groupby("fc_hz").src_esd_db.agg(["mean", "count"]); pb = pb[pb["count"] >= 2]
    c, _ = ols(np.log2(pb.index.values), pb["mean"].values)
    for tri in ("H11N", "H11S"):
        for fc in (2.0, 2.5, 3.15, 4.0):
            q = g[(g.triad == tri) & (g.fc_hz == fc)]; qm = q[q.measured]
            ex = c[0] + c[1] * np.log2(fc)
            CAV.append(dict(chain=chn, src_depth_m=zs, triad=tri, fc_hz=fc, n_measured=len(qm), src_esd_measured_mean_db=qm.src_esd_db.mean() if len(qm) else np.nan,
                            powerlaw_extrapolation_db=ex, excess_over_powerlaw_db=(qm.src_esd_db.mean() - ex) if len(qm) else np.nan))
CAVd = pd.DataFrame(CAV)
cavity_supported = bool(((CAVd.groupby(["chain", "src_depth_m", "triad"]).excess_over_powerlaw_db.max() >= 3).groupby(["chain", "src_depth_m"]).all()).any())
def shape_db(fcs, fr, n):
    bfr = np.array([float(band_fraction(fc, np.array([fr]), n)[0]) for fc in fcs]); bw = np.array([fc * (2 ** (1 / 6) - 2 ** (-1 / 6)) for fc in fcs])
    return 10 * np.log10(bfr / bw)
FC = []
FRG = np.round(np.arange(1.0, 10.01, 0.25), 2); NG = np.arange(2.0, 5.01, 0.05)
for (chn, zs), g in SS[SS.measured & SS.fc_hz.between(3.0, 63)].groupby(["chain", "src_depth_m"]):
    pb = g.groupby("fc_hz").src_esd_db.agg(["mean", "count"]); pb = pb[pb["count"] >= 2]; f_ = pb.index.values; y = pb["mean"].values
    grid = {(fr, n): np.sum((y - shape_db(f_, fr, n) - np.mean(y - shape_db(f_, fr, n))) ** 2) for fr in FRG for n in NG}
    (fr0, n0), r0 = min(grid.items(), key=lambda kv: kv[1]); s2 = r0 / max(len(y) - 3, 1)
    prof = {fr: min(v for (a, n), v in grid.items() if a == fr) for fr in FRG}; ok = [fr for fr, v in prof.items() if (v - r0) / s2 <= 1.0]
    FC.append(dict(chain=chn, src_depth_m=zs, corner_hz=fr0, exponent_above_corner=n0, corner_lo_hz=min(ok), corner_hi_hz=max(ok), rms_db=float(np.sqrt(r0 / len(y))), n_bands=len(y),
                   bands=" ".join(f"{v:g}" for v in f_)))
FCd = pd.DataFrame(FC)

# ---------------- R4 D1 ridge
TAU = PR.TAU_FALLBACK; RHO_C = PR.RHO_C
B12 = PR.BANDS; W12 = np.array([PR.W63 if fc == 63.0 else 1.0 for fc in B12]); B18 = RL.BANDS; W18 = np.ones(len(B18))
nfit = {(r.chain, r.src_depth_m): -r.src_esd_slope_db_oct / (10 * np.log10(2)) for r in SLd[(SLd.who == "pooled") & (SLd.band == "5-63")].itertuples()}
fcfit = {(r.chain, r.src_depth_m): (r.corner_hz, r.exponent_above_corner) for r in FCd.itertuples()}
def fam_params(fam, chn, zs):
    return {"F2": (1 / TAU, 2.0), "F4": (1 / TAU, 4.0), "Ffit": (1 / TAU, nfit[(chn, zs)]), "Ffit_c": fcfit[(chn, zs)]}[fam]
_sb = {}
def sbv(bands, fr, n):
    k = (tuple(bands), round(fr, 4), round(n, 4))
    if k not in _sb: _sb[k] = np.array([float(band_fraction(fc, np.array([fr]), n)[0]) for fc in bands])
    return _sb[k]
SE5 = {el: OBS[el]["se_pa2s"] for el in RL.ELS}; SE18 = {el: float(BD[BD.element == el].excess_pa2s.sum()) for el in RL.ELS}
rows = []
for fam in ("F2", "F4", "Ffit", "Ffit_c"):
    for chn in ("KRAKEN_ONLY", "KRAKEN_RAM"):
        for zs in DEPTHS:
            fr, n = fam_params(fam, chn, zs)
            for src in ("W", "P"):
                for score, bands, Wt, SE in (("5-63", B12, W12, SE5), ("2-100", B18, W18, SE18)):
                    s = sbv(bands, fr, n)
                    for ramsrc in (("module", "own_new") if (chn == "KRAKEN_RAM" and src == "W" and RAMNEW is not None) else ("module",)):
                        for el in RL.ELS:
                            Gk = RHO_C / (2 * np.pi) * np.sum(Wt * s * 10 ** (-tlv(f"{src}-{el[:4]}", zs, chn, bands, ramsrc) / 10))
                            for ek, E in EJ.items():
                                rows.append(dict(family=fam, chain=chn, ram_delta=ramsrc if chn == "KRAKEN_RAM" else "none", src_depth_m=zs, src=src, score=score, element=el,
                                                 triad=el[:4], E=ek, Ej=E, fr_hz=fr, n_exp=n, se=SE[el], G=Gk, eta=SE[el] / (E * Gk)))
ETA = pd.DataFrame(rows)
keys = ["family", "chain", "ram_delta", "src_depth_m", "src", "score", "E"]
TR = ETA.groupby(keys + ["triad"]).agg(se=("se", "mean"), G=("G", "first"), Ej=("Ej", "first")).reset_index(); TR["eta"] = TR.se / (TR.Ej * TR.G)
PO = TR.groupby(keys).eta.apply(lambda v: float(np.exp(np.log(v).mean()))).rename("eta").reset_index()
sE = 0.5 * np.log(1100 / 700)
def pick(df, **k):
    m = np.logical_and.reduce([(df[c] == v) if not isinstance(v, float) else np.isclose(df[c], v) for c, v in k.items()]); return df[m]
RID = []
for (fam, chn, rd, zs, score), g in ETA[(ETA.E == "mid") & (ETA.src == "W")].groupby(["family", "chain", "ram_delta", "src_depth_m", "score"]):
    po = lambda src, E="mid": float(pick(PO, family=fam, chain=chn, ram_delta=rd if src == "W" else ("module" if chn == "KRAKEN_RAM" else "none"), src_depth_m=zs, src=src, score=score, E=E).eta.iloc[0])
    tr = pick(TR, family=fam, chain=chn, ram_delta=rd, src_depth_m=zs, src="W", score=score, E="mid").set_index("triad").eta
    le = np.log(g.set_index("element").eta)
    s_el = float(np.sqrt(np.mean([le[[t + str(i) for i in (1, 2, 3)]].var(ddof=1) for t in ("H11N", "H11S")])) / np.sqrt(3))
    s_st = float(abs(np.log(tr["H11N"] / tr["H11S"])) / 2); s_loc = float(abs(np.log(po("P") / po("W")))); s_tot = float(np.sqrt(sE ** 2 + s_el ** 2 + s_st ** 2 + s_loc ** 2))
    eta = po("W")
    RID.append(dict(family=fam, chain=chn, ram_delta=rd, src_depth_m=zs, score_band_hz=score, eta_pooled=eta, eta_H11N=tr["H11N"], eta_H11S=tr["H11S"],
                    eta_element_min=g.eta.min(), eta_element_max=g.eta.max(), eta_at_P=po("P"), eta_E700=po("W", "low"), eta_E1100=po("W", "high"),
                    sig_ln_energy=sE, sig_ln_element=s_el, sig_ln_station=s_st, sig_ln_location=s_loc, sig_ln_total=s_tot,
                    eta_low_68=eta * np.exp(-s_tot), eta_high_68=eta * np.exp(s_tot), corner_hz=g.fr_hz.iloc[0], exponent=g.n_exp.iloc[0], energy_admissible=bool(eta < 1.0)))
RD = pd.DataFrame(RID)
kk = RD[RD.ram_delta != "own_new"].set_index(["family", "chain", "src_depth_m", "score_band_hz"]).eta_pooled
RD["ratio_RAM_over_KRAKEN"] = [kk[(r.family, "KRAKEN_RAM", r.src_depth_m, r.score_band_hz)] / kk[(r.family, "KRAKEN_ONLY", r.src_depth_m, r.score_band_hz)] for r in RD.itertuples()]
RD["ratio_family_over_F2"] = [r.eta_pooled / kk[("F2", r.chain, r.src_depth_m, r.score_band_hz)] for r in RD.itertuples()]

# ---------------- R5 D4 in-band, R6 D2 Arons
D4 = []
for chn in ("KRAKEN_ONLY", "KRAKEN_RAM"):
    for zs in DEPTHS:
        for el in RL.ELS:
            b = BD[BD.element == el].set_index("fc_hz"); tl18 = tlv("W-" + el[:4], zs, chn, B18); tl12 = tlv("W-" + el[:4], zs, chn, B12)
            e12 = np.clip(b.loc[B12].excess_pa2s.values, 0, None) * W12; seb = e12 / e12.sum() * SE5[el]
            msk = b.loc[B18].measured.values; e18 = b.loc[B18].excess_pa2s.values
            D4.append(dict(chain=chn, src_depth_m=zs, element=el, triad=el[:4], Eac_4_64_J=2 * np.pi / RHO_C * np.sum(seb * 10 ** (tl12 / 10)),
                           Eac_measured_2_100_J=2 * np.pi / RHO_C * np.sum((e18 * 10 ** (tl18 / 10))[msk])))
D4d = pd.DataFrame(D4)
D4t = D4d.groupby(["chain", "src_depth_m", "triad"])[["Eac_4_64_J", "Eac_measured_2_100_J"]].mean().reset_index()
D4p = D4t.groupby(["chain", "src_depth_m"])[["Eac_4_64_J", "Eac_measured_2_100_J"]].apply(lambda g: np.exp(np.log(g).mean())).reset_index()
D4p["eta_D4_4_64"] = D4p.Eac_4_64_J / 900e6; D4p["eta_D4_measured_2_100"] = D4p.Eac_measured_2_100_J / 900e6
D4p["triad_min_4_64"] = [pick(D4t, chain=r.chain, src_depth_m=r.src_depth_m).Eac_4_64_J.min() / 900e6 for r in D4p.itertuples()]
D4p["triad_max_4_64"] = [pick(D4t, chain=r.chain, src_depth_m=r.src_depth_m).Eac_4_64_J.max() / 900e6 for r in D4p.itertuples()]
Rkm = {t: float(T[T.path == f"W-{t}"].range_km.iloc[0]) for t in ("H11N", "H11S")}
D2 = []
for el in RL.ELS:
    o = OBS[el]
    for lab, key in (("2-100 Hz instantaneous", "ipk_2_100_pa"), ("4-64 Hz instantaneous", "ipk_4_64_pa"), ("4-40 Hz instantaneous", "ipk_4_40_pa"),
                     ("1-110 Hz instantaneous (response removal only)", "ipk_resp_only_pa"), ("4-64 Hz 1-s RMS peak", None)):
        Pp = 10 ** (o["peak_db"] / 20) * 1e-6 if key is None else o[key]; Wk = RL.arons_w_kg(Pp, Rkm[el[:4]] * 1e3)
        D2.append(dict(element=el, triad=el[:4], peak_definition=lab, P_pa=Pp, R_km=Rkm[el[:4]], W_tnt_kg=Wk, eta_D2=Wk * 4.184e6 / 900e6,
                       eta_D2_E1100=Wk * 4.184e6 / 1100e6, eta_D2_E700=Wk * 4.184e6 / 700e6))
D2d = pd.DataFrame(D2)
D2s = D2d.groupby("peak_definition").agg(P_min_pa=("P_pa", "min"), P_max_pa=("P_pa", "max"), eta_min=("eta_D2", "min"), eta_max=("eta_D2", "max"),
                                         eta_gmean=("eta_D2", lambda v: float(np.exp(np.log(v).mean()))), eta_lo_E1100=("eta_D2_E1100", "min"), eta_hi_E700=("eta_D2_E700", "max")).reset_index()

# ---------------- write
B.to_csv(OUT / "f35a-raw-bazimuth-windows.csv", index=False); BS.to_csv(OUT / "f35a-raw-bazimuth.csv", index=False)
BD.to_csv(OUT / "f35a-raw-band-exposure.csv", index=False); GD.to_csv(OUT / "f35a-raw-gap-test.csv", index=False)
SS.to_csv(OUT / "f35a-raw-source-spectrum.csv", index=False); SLd.to_csv(OUT / "f35a-raw-source-slope.csv", index=False)
CAVd.to_csv(OUT / "f35a-raw-lowfreq-check.csv", index=False); FCd.to_csv(OUT / "f35a-raw-corner-fit.csv", index=False)
ETA.to_csv(OUT / "f35a-raw-eta-elements.csv.gz", index=False); RD.to_csv(OUT / "f35a-raw-ridge.csv", index=False)
D4p.to_csv(OUT / "f35a-raw-d4.csv", index=False); D2d.to_csv(OUT / "f35a-raw-d2-elements.csv", index=False); D2s.to_csv(OUT / "f35a-raw-d2.csv", index=False)
spec_rows = [dict(element=el, f_hz=float(fq), arrival_psd_db=10 * np.log10(s["Pa"][i] / 1e-12), noise_pre_psd_db=10 * np.log10(s["Pn"][i] / 1e-12),
                  bg_p05_psd_db=10 * np.log10(s["bg5"][i] / 1e-12), bg_p50_psd_db=10 * np.log10(s["bg50"][i] / 1e-12), bg_p95_psd_db=10 * np.log10(s["bg95"][i] / 1e-12),
                  excess_esd_pa2s_hz=float(s["esd"][i]), window_s=s["Wlen"]) for el, s in SPEC.items() for i, fq in enumerate(s["f"]) if fq <= 125]
pd.DataFrame(spec_rows).to_csv(OUT / "f35a-raw-spectra.csv", index=False)
pickle.dump(dict(OBS={k: {kk: v for kk, v in o.items()} for k, o in OBS.items()}, GEO=GEO, coords=coords, G2_response_gap_db=G2, cavity_supported=cavity_supported,
                 Rkm=Rkm, nfit=nfit, fcfit=fcfit), open(OUT / "analysis.pkl", "wb"))
print(json.dumps(dict(G2_response_gap_db=G2, cavity_supported=cavity_supported, ram_new_used=RAMNEW is not None), indent=1))
print(BS.round(3).to_string()); print(GD.round(2).to_string())
print(RD[(RD.score_band_hz == "5-63") & (RD.family == "F2")][["chain", "ram_delta", "src_depth_m", "eta_pooled", "eta_low_68", "eta_high_68"]].to_string())
