D="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat > "$D/prepare/ranked_candidates/rank.py" <<'EOF'
"""EXPLORATORY ranking of the run J search candidates (graphics track 22 Oct 2026). Implements prereg.py (commit 9f47cf7).
Run from the module root:  python prepare/ranked_candidates/rank.py  (about 12 min, ~13 GB RAM, single process).
Writes results-data/ranked_candidates/{ranked_singles,ranked_pairs,ranked_triples,ranked_multisite}.csv and detectability.json.
This file is the consolidated form of the interactive session that produced the committed tables (same code, same seed).
PREDICTIVE, NOT CALIBRATED; C1, C2. Not part of the frozen searches.
"""
import os, sys, json, itertools, collections, importlib.util
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from pyproj import Geod
HERE = Path(__file__).resolve().parent; MOD = HERE.parent.parent
sys.path.insert(0, str(MOD / "prepare" / "composition_run_j")); sys.path.insert(0, str(MOD / "prepare"))
import prereg as R; import common as Cm; import run_j_windows as Wm
spec = importlib.util.spec_from_file_location("rprereg", HERE / "prereg.py"); P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
EX = Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches"); OUT = MOD / "results-data" / "ranked_candidates"; OUT.mkdir(exist_ok=True)
G = Geod(ellps="WGS84"); M = Cm.Machinery(imos_ramgrid=True); T0 = R.T0; ANCH = R.ETA_ANCHOR
S = dict(np.load(EX / "geometry/sample.npz")); anyw = (S["w_D0"] > 0) | (S["w_D2"] > 0) | (S["w_D3"] > 0) | (S["w_D4"] > 0); idx = np.where(anyw)[0]
lat, lon, t, E, tau = [S[k][idx] for k in ["lat", "lon", "t_unix", "E_j", "tau90_s"]]; Wt = {o: S[f"w_{o}"][idx] for o in R.OPTIONS}; w0 = Wt["D0"]
PP = M.prep(t, lat, lon, E, tau); rng = np.random.default_rng(P.SEED); Lcal = rng.normal(0, R.CAL_L_SD_DB, len(t))
rl, ro = M.rxpos["H01W"]; baz = np.mod(G.inv(np.full_like(lon, ro), np.full_like(lat, rl), lon, lat)[0], 360)
order = {rx: np.argsort(PP["tp"][rx]) for rx in R.RECEIVERS}; tps = {rx: PP["tp"][rx][order[rx]] for rx in R.RECEIVERS}
ETA = np.logspace(np.log10(P.ETA_LO), np.log10(P.ETA_HI), P.N_ETA); L10 = 10 * np.log10(ETA); ALS = [0.001, 0.01, 0.05, 0.1, 0.3]; WIN = 60.0
def pd_params(rx, method, alpha):
    la = np.log10(np.clip(alpha, *P.ALPHA_CLIP)); out = []
    for tt in M.taus:
        L, Sl, A = [], [], []
        for al in ALS:
            f = M.fits.get(f"{rx}|{method}|{al}|{tt}", {})
            if f.get("L50_re_noise_db") is not None and f.get("slope_db") is not None: L.append(f["L50_re_noise_db"]); Sl.append(f["slope_db"]); A.append(np.log10(al))
        out.append((np.interp(la, A, L), np.interp(la, A, Sl)) if A else (np.nan, np.nan))
    return np.array(out)
ic = pd.read_csv(EX / "imos/imos_candidates.csv", dtype={"receiver": str}); pc = pd.read_csv(EX / "panels/panel_candidates.csv"); t1 = pd.read_csv(EX / "named/table1_verdicts.csv")
t1["t_unix"] = [Cm.hms_to_unix(s) for s in t1.time_utc]
cand = [dict(rx=r.receiver, time_utc=r.time_utc, t_unix=r.t_unix, det=r.detector, band=r.band_hz, p=r.p, p_B=np.nan, label=r.label, excess=r.excess_5_40_pa2s,
             eta_needed_searches=r.eta_needed, kadri_label=r.kadri_label, source="IMOS raw recording") for r in ic.itertuples()]
cand += [dict(rx=r.receiver, time_utc=r.time_utc, t_unix=r.t_unix, det=r.detector, band=r.band_hz, p=r.p, p_B=r.p_B, label=r.label, excess=np.nan,
              eta_needed_searches=r.eta_needed, kadri_label=r.kadri_label, source="digitised Kadri (2024) Fig. 9 panel " + r.panel) for r in pc.itertuples()]
C = pd.DataFrame(cand); C["key"] = C.rx + "|" + C.time_utc + "|" + C.det + "|" + C.band; C["cid"] = [f"{k}|p{p:.6g}" for k, p in zip(C.key, C.p)]
tpj = json.load(open(R.RD / "tl_grid_run_j" / "table_points.json")); arc = sorted([(v["lat"], v["lon"]) for v in tpj.values() if v["offset_nm"] == 0])
ARC_LA = np.array([a for a, b in arc]); ARC_LO = np.array([b for a, b in arc])
bref, tiref = M.level_base(np.array([P.REF_LAT]), np.array([P.REF_E_J]), np.array([P.REF_TAU_S]))
def so_rows(c, rows):
    rx = c["rx"]
    if rx in R.RECEIVERS_GATED and np.isfinite(c["excess"]) and c["excess"] > 0: return 10 * (np.log10(c["excess"]) + 12 - np.log10(M.teff[rx][PP["ti"][rows]])) - M.bmed[rx]
    if np.isfinite(c["eta_needed_searches"]): return np.full(len(rows), bref[rx][0] + 10 * np.log10(c["eta_needed_searches"]))
    return np.full(len(rows), np.nan)
def so_at(c, ti0):
    rx = c["rx"]
    if rx in R.RECEIVERS_GATED and np.isfinite(c["excess"]) and c["excess"] > 0: return 10 * (np.log10(c["excess"]) + 12 - np.log10(M.teff[rx][ti0])) - M.bmed[rx]
    return bref[rx][0] + 10 * np.log10(c["eta_needed_searches"])
C["eta_level_ref"] = [np.inf if c["rx"] not in R.RECEIVERS else float(10 ** ((so_at(c, tiref[0]) - bref[c["rx"]][0]) / 10)) for _, c in C.iterrows()]
def rows_for(rx, tc):
    a = np.searchsorted(tps[rx], tc - WIN); b = np.searchsorted(tps[rx], tc + WIN); r = order[rx][a:b]; return r[np.isfinite(PP["base"][rx][r])]
def factor(c, rows, bearing=None):
    rx = c["rx"]; d = PP["d"][rx][rows]; sig = np.sqrt((d * R.C_SOFAR_SD / R.C_SOFAR ** 2) ** 2 + R.SIGMA_INJ_S ** 2 + R.SIGMA_CLOCK_S ** 2)
    z = (PP["tp"][rx][rows] - c["t_unix"]) / sig; K = np.where(np.abs(z) <= R.KERNEL_TRUNC_SIGMA, np.exp(-0.5 * z * z) / (np.sqrt(2 * np.pi) * sig), 0.0)
    par = pd_params(rx, P.DETECTOR_METHOD[c["det"]], c["p"]); ti = PP["ti"][rows]; snr = PP["base"][rx][rows][:, None] + L10[None, :] + Lcal[rows][:, None]
    with np.errstate(over="ignore"): pdv = np.nan_to_num(1 / (1 + np.exp(-(snr - par[ti, 0][:, None]) / par[ti, 1][:, None])), nan=0.0)
    so = so_rows(c, rows); A = np.exp(-0.5 * ((snr - so[:, None]) / P.SIGMA_A_DB) ** 2) if np.isfinite(so).all() else np.ones_like(snr)
    brs = bearing if bearing is not None else (list(t1.bearing_deg[np.abs(t1.t_unix - c["t_unix"]) <= P.BEARING_WINDOW_S]) if rx == "H01W" else [])
    Gb = np.mean([stats.t.pdf(((b - baz[rows] + 180) % 360 - 180) / P.BEARING_T3_SCALE_DEG, 3) / P.BEARING_T3_SCALE_DEG * 360 for b in brs], axis=0) if len(brs) else np.ones(len(rows))
    return K[:, None] * pdv * A * Gb[:, None], K, brs
def score_set(cs, bearing_override=None):
    lnB = float(np.sum([np.log(c["p"] / R.WINDOW_S) for c in cs]))
    lnBpB = float(np.sum([np.log((c["p_B"] if np.isfinite(c["p_B"]) else c["p"]) / R.WINDOW_S) for c in cs]))
    if any(c["rx"] not in R.RECEIVERS for c in cs): return dict(lnN=-np.inf, lnB=lnB, lnB_pB=lnBpB, blocked=True)
    rows = rows_for(cs[0]["rx"], cs[0]["t_unix"])
    for c in cs[1:]: rows = rows[(np.abs(PP["tp"][c["rx"]][rows] - c["t_unix"]) <= WIN) & np.isfinite(PP["base"][c["rx"]][rows])]
    if len(rows) == 0: return dict(lnN=-np.inf, ln_ftime=-np.inf, lnB=lnB, lnB_pB=lnBpB, blocked=False, n_rows=0)
    Fp = np.ones((len(rows), len(ETA))); Kp = np.ones(len(rows)); allb = []
    for c in cs:
        F, K, brs = factor(c, rows, bearing_override if (bearing_override is not None and c["rx"] == "H01W") else None); Fp *= F; Kp *= K; allb += brs
    fm = Fp.mean(1); out = dict(blocked=False, n_rows=int((Kp > 0).sum()), bearings=";".join(f"{b:.2f}" for b in allb), lnB=lnB, lnB_pB=lnBpB)
    for o in R.OPTIONS: out[f"lnN_{o}"] = np.log(max((Wt[o][rows] * fm).sum(), 1e-300))
    w = w0[rows]; N = (w * fm).sum(); ft = (w * Kp).sum(); out.update(lnN=np.log(N) if N > 0 else -np.inf, ln_ftime=np.log(ft) if ft > 0 else -np.inf)
    if N > 0:
        ww = w * fm / N
        out.update(src_lat=float((ww * lat[rows]).sum()), src_lon=float((ww * lon[rows]).sum()), src_t=float((ww * t[rows]).sum()),
                   src_E_med=float(np.interp(0.5, np.cumsum(ww[np.argsort(E[rows])]), np.sort(E[rows]))),
                   eta_post_med=float(10 ** np.interp(0.5, np.cumsum((w[:, None] * Fp).sum(0)) / (w[:, None] * Fp).sum(), np.log10(ETA))),
                   baz_H01W=float(np.degrees(np.angle((ww * np.exp(1j * np.radians(baz[rows]))).sum())) % 360))
    return out
# arc loci and coupling requirement (block 11 coincidence method generalised)
rxall = Wm.receivers(); fla = np.linspace(ARC_LA.min(), ARC_LA.max(), 2001); flo = np.interp(fla, ARC_LA, ARC_LO)
DARC = {rx: G.inv(flo, fla, np.full_like(flo, v[1]), np.full_like(fla, v[0]))[2] / 1000 for rx, v in rxall.items()}
def hms(u): s = u - T0; return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:04.1f}"
def mass1(L_): m = np.abs(lat - L_) <= 1.0; return float(w0[m].sum()), np.where(m)[0]
lg = np.linspace(-6, 0, 601)
def eta_req(cs, L_):
    if any(c["rx"] not in R.RECEIVERS for c in cs): return np.inf, np.inf, np.nan
    ms, m = mass1(L_)
    if len(m) < 20: return np.nan, np.nan, ms
    w = w0[m]; Em = float(np.interp(0.5, np.cumsum(w[np.argsort(E[m])]) / w.sum(), np.sort(E[m]))); tm = float(np.interp(0.5, np.cumsum(w[np.argsort(tau[m])]) / w.sum(), np.sort(tau[m])))
    base, ti = M.level_base(np.array([L_]), np.array([Em]), np.array([tm])); both = np.ones_like(lg); lvl = []
    for c in cs:
        par = pd_params(c["rx"], P.DETECTOR_METHOD[c["det"]], 0.05)[ti[0]]; both *= 1 / (1 + np.exp(-(base[c["rx"]][0] + 10 * lg - par[0]) / par[1]))
        lvl.append(10 ** ((so_at(c, ti[0]) - base[c["rx"]][0]) / 10))
    k = np.argmax(both >= 0.5) if (both >= 0.5).any() else None
    return (10 ** lg[k] if k is not None else np.inf), max(lvl), ms
def locus_cols(cs):
    lagp = (DARC[cs[1]["rx"]] - DARC[cs[0]["rx"]]) / R.C_SOFAR; target = cs[1]["t_unix"] - cs[0]["t_unix"]; loc = []
    for i in np.where(np.diff(np.sign(lagp - target)) != 0)[0]:
        L_ = float(np.interp(target, [lagp[i], lagp[i + 1]], [fla[i], fla[i + 1]])) if lagp[i + 1] != lagp[i] else fla[i]
        loc.append((L_, float(np.interp(L_, fla, flo)), cs[0]["t_unix"] - np.interp(L_, fla, DARC[cs[0]["rx"]]) / R.C_SOFAR))
    if len(cs) == 3: loc = [x for x in loc if abs(x[2] + np.interp(x[0], fla, DARC[cs[2]["rx"]]) / R.C_SOFAR - cs[2]["t_unix"]) <= 60]
    out = dict(n_arc_loci=len(loc))
    if not loc: return out
    ms = [mass1(x[0])[0] for x in loc]; j = int(np.argmax(ms)); L_, lo_, ti_ = loc[j]; e50, elv, _ = eta_req(cs, L_)
    out.update(locus_lat=L_, locus_lon=lo_, implied_impact_utc=hms(ti_), implied_vs_0019="after" if ti_ > R.T_0019_LOGON else "BEFORE 00:19:29", locus_D0_mass_within_1deg=ms[j],
               eta_pd50_all_a005=e50, eta_level_locus=elv, other_loci=";".join(f"{a:.2f}S {b:.2f}E {hms(c)}" for k, (a, b, c) in enumerate(loc) if k != j))
    if any(c["rx"] == "H01W" for c in cs): out["locus_baz_H01W"] = G.inv(rxall["H01W"][1], rxall["H01W"][0], lo_, L_)[0] % 360
    return out
if __name__ == "__main__":
    CID = C.set_index("cid")
    SG = pd.DataFrame([{**c, **score_set([c])} for c in C.to_dict("records")])
    SG["lnLR"] = SG.lnN - SG.lnB; SG["lnLR_no_bearing"] = SG.lnLR
    for i in SG.index[SG.rx == "H01W"]: SG.loc[i, "lnLR_no_bearing"] = score_set([SG.loc[i].to_dict()], [])["lnN"] - SG.loc[i, "lnB"]
    pr = pd.read_csv(EX / "coincidence/pairs.csv", dtype={"rx_a": str, "rx_b": str}); kk = ["rx_a", "t_a", "det_a", "band_a", "p_a", "rx_b", "t_b", "det_b", "band_b", "p_b"]
    pu = pr.groupby(kk, as_index=False).agg(family=("family", lambda x: "+".join(sorted(set(x)))), lag_s=("lag_s", "first"), lag_lo_s=("lag_lo_s", "first"), lag_hi_s=("lag_hi_s", "first"), max_p=("max_p", "first"))
    def find(rx, tt, det, band, p): m = C[(C.key == f"{rx}|{tt}|{det}|{band}") & np.isclose(C.p, p, rtol=1e-6)]; return m.iloc[0].to_dict()
    prow = []
    for r in pu.itertuples():
        a = find(r.rx_a, r.t_a, r.det_a, r.band_a, r.p_a); b = find(r.rx_b, r.t_b, r.det_b, r.band_b, r.p_b)
        s = score_set([a, b]); s["lnLR_no_bearing"] = (score_set([a, b], [])["lnN"] - s["lnB"]) if "H01W" in (a["rx"], b["rx"]) else None
        prow.append({**r._asdict(), "cid_a": a["cid"], "cid_b": b["cid"], **s, **locus_cols([a, b])})
    PRS = pd.DataFrame(prow); PRS["lnLR"] = PRS.lnN - PRS.lnB
    adj = collections.defaultdict(set)
    for a, b in zip(PRS.cid_a, PRS.cid_b): adj[a].add(b); adj[b].add(a)
    tri = sorted({tuple(sorted((a, b, c))) for a in adj for b, c in itertools.combinations(sorted(adj[a]), 2) if c in adj[b] and len({x.split("|")[0] for x in (a, b, c)}) == 3})
    trows = []
    for trp in tri:
        cs = sorted([dict(CID.loc[x].to_dict(), cid=x) for x in trp], key=lambda c: ({"H01W": 0, "H08S": 1}.get(c["rx"], 2), c["t_unix"]))
        s = score_set(cs); d = dict(cids=" & ".join(c["cid"] for c in cs), **s)
        if not s.get("blocked"): d.update(locus_cols(cs))
        trows.append(d)
    TR = pd.DataFrame(trows); TR["lnLR"] = TR.lnN - TR.lnB
    for n, d in [("ranked_singles", SG), ("ranked_pairs", PRS), ("ranked_triples", TR)]: d.sort_values("lnLR", ascending=False).to_csv(OUT / f"{n}_raw.csv", index=False)
EOF
python -c "import ast;ast.parse(open('$D/prepare/ranked_candidates/rank.py').read())" && echo ok