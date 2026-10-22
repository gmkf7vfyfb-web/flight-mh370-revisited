"""Arrival-time windows at every receiver from end of flight's run J (block 3, timing half, of the 21 Oct 2026 work order).

PRE-REGISTERED (overnight 21/22 Oct 2026). Committed to hypothesis/hydroacoustics before any run on the run J impacts.
The rules below are fixed; anything changed after the run is an amendment, committed and disclosed in the results note.

IMPACT SET. Run J, four strata on disk (mh370-exchange/end-of-flight/run-j/<stratum>/seed-N/impacts32.npy, compact
  float32 v1, times in seconds after T0 = 1394236800 = 00:00:00 UTC 8 Mar 2014): run-j-waypoints (24 seeds), run-j-free
  (18), run-j-descent-climb (16), run-j-repro-radar (16); 313,599,968 rows. Plus the northern supplement
  end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz, rows with technique >= 1 only (technique 0 rows are the
  production set already covered by the strata). Convergence of run J: accepted as a pass by project ruling, 16 Oct 2026.

00:19 OPTIONS and WEIGHTS (end of flight's own two-factor table, smoke/option_table_0019.py, "total q = 1/3 (C2 silent)"
  cells, the same convention as the supplement's lnw:comb/<D> columns; re-implemented here from the stored columns):
    ln w_row = ln(weight / sum weight) + ln(1 - P_breakup_to_0019) + ld_D + ln( 0.75 exp(C1) + 0.25 exp(C2) )
    ld_D:  D0' = 0 (00:19 values held out); D2 = loglik:r600/no-offset; D3 = loglik:both/no-offset;
           D4 = loglik:both/startup-offset  (NaN loglik -> row weight 0)
    C1 (fuel exhaustion + APU start): Erlang(lag_shape, lag_scale_s) density of logon_unix_s - realised flame-out (run.json
           [config] end-of-flight.logon), plus the existence constraint `unpowered`: impact after 00:19:37.443, and not
           still powered at 01:15:56 (impact after 01:15:56 with no flame-out before it -> excluded).
    C2 (other cause, `silent`): -ln W (W = 3,898 s, 00:10:58 to 01:15:56) plus `unpowered` plus the no-later-log-on
           survival ln Q(lag_shape, (impact - flame-out) / lag_scale_s) where the flame-out is finite.
  Survival factor (no in-flight breakup before 00:19:37) applied throughout, as end of flight does (architecture 20:55Z 11 Oct).
  POOLING: seeds pooled by evidence as end of flight pools them: row weight x p_core(stratum) / K(stratum), K the seed
  count, p_core from summary/family-evidence-run-j.json (0.9982 / 0.0013 / 0.0003 / 0.0002). The stratum share under
  each option is therefore p_core x Zhat_D (re-weighted by the 00:19 evidence), the same as EoF's table.
  SUPPLEMENT: rows with technique >= 1, weight exp(lnw:comb/<D>); its share of the total, s_D = sum of those weights (the
  file is normalised over production + supplement), is taken as its share of the final mixture:
    F = (1 - s_D) F_strata + s_D F_supplement.
DIVE PROBABILITY p in {0, 0.5, 1} (0.5 primary): the module's existing re-weighting (kadri_northern_conditional.py): each
  row's weight is multiplied by 2p where latent:pushover_to_surface = 1, by 2(1 - p) where latent:pushover_drawn = 1 and
  pushover_to_surface = 0, and by 1 where pushover_drawn = 0. The supplement file has no pushover_to_surface column, so its
  rows keep their native (p = 0.5 proposal) weights at every p: DECLARED GAP, its size is s_D.
RECEIVERS. IMS triads H01W, H08S, H08N at the mean of their element positions (data/stations.csv); IMOS loggers 3315, 3376
  (Perth Canyon), 3274, 3275 (Portland), 3250 (Scott Reef, declared no-information row) at data/ocean_paths/request.json
  endpoints; OHASISBIO 2014 sites NEAMS, SWAMS (SWAMS-2), SSEIR, MAD, WKER, NCRO at the positions in
  results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md (chart rows marked "no recordings held").
ARRIVAL MODEL (as search_windows.py, prereg 55eb191): d = WGS84 geodesic impact -> receiver;
  SOFAR  t_arr = t_impact + d / c, c ~ N(1.482, 0.006) km/s, one draw per row shared by all receivers;
  AGW    t_arr = t_impact + d / c, c ~ U(1.40, 1.50) km/s per row. ASSUMPTION, not modelled (no mode group speed yet).
  No refraction, blockage or path lengthening. rng = default_rng([20261021, stratum_index, seed]).
GRID. 2 s bins from 23:00:00 UTC 7 Mar to 06:00:00 UTC 8 Mar 2014 (12,600 bins); mass beyond the grid is reported.
QUANTILES (weighted, from the pooled CDF): 0.5, 5, 25, 50, 75, 95, 99.5 %. INTERVALS: 50 % = [q25, q75], 90 % = [q5, q95],
  99 % = [q0.5, q99.5]. REQUEST WINDOW: [q0.5 - 10 min, q99.5 + 20 min], start floored and end ceiled to 5 min; recommended
  request per receiver = union over the four options with pooled ESS >= 1,000 (Kish ESS = (sum w)^2 / sum w^2 over every
  row of the mixture, supplement included), per branch, at p = 0.5; p = 0 and 1 beside it.
CONVERGENCE FLAG: per-seed q0.5 and q99.5 of the waypoints stratum (99.8 % of the mixture mass); a spread (max - min)
  over its 24 seeds above 5 min flags the row UNCONVERGED (tail), as in search_windows.py. Reported, not hidden.
HELD-DATA COVERAGE: the fraction of impact-time mass whose SOFAR (and AGW) arrival falls inside a recording the module
  holds: IMOS = the 307 s records in data/imos/recordings.csv (start_logger, dur_s) per logger; H01W = Kadri (2024) Fig. 9
  panels a-c (00:27-00:57, digitised traces); H08S = panels d-e (01:00-01:20); H08N, OHASISBIO = nothing held (0).
  Blackman et al. (2004) is 2003 data: n/a.
NORTHERN EXTENT: the 99th-percentile latitude of the impact mass per option (rule 7 of the operating note); the arc proxy
  for the publication-coverage chart is the weighted median impact longitude per 0.5 deg latitude bin (D0', p = 0.5).
LABELS carried by every output: source posterior run J (+ northern supplement); 00:19 option; p; SOFAR / AGW branch;
  PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2
  (coupling efficiency not calibrated) apply to any level statement built on these windows; both Kadri times, "text time
  00:52:03" and "caption time 00:54:30", wherever Kadri's event is marked.
OUTPUTS (exchange, mh370-exchange/hydroacoustics/run-j-windows/): per seed <stratum>/seed-N.npz (histograms, sums,
  quantiles), supplement.npz, pooled.npz, windows.csv, coverage.csv, run.json. The repository copy (results-data/
  windows_run_j/) carries windows.csv, coverage.csv, ess.csv and run.json only.

Usage (from prepare/, PYTHONPATH=.):
  python run_j_windows.py seeds   --eof <run-j root> --out <exchange dir> [--workers 2] [--strata ...]
  python run_j_windows.py supplement --supp <impacts-ruleB.npz> --out <exchange dir>
  python run_j_windows.py pool    --eof <run-j root> --out <exchange dir> --repo-out <results-data/windows_run_j>
"""
import argparse, csv, hashlib, json, os, pathlib, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE.parent
T0 = 1394236800.0                 # 00:00:00 UTC 8 Mar 2014
T_M0019B = 1394237977.443         # 00:19:37.443
T_LOI_0115 = 1394241356.0         # 01:15:56
W_S = 1394241356.0 - 1394237458.0 # 3,898 s
Q_MIX = 1.0 / 3.0; P_C1 = 1.0 / (1.0 + Q_MIX)
GRID0, GRID1, DT = T0 - 3600.0, T0 + 21600.0, 2.0
NBIN = int((GRID1 - GRID0) / DT)
C_SOFAR, C_SOFAR_SD = 1.482, 0.006
C_AGW = (1.40, 1.50)
QS = [0.005, 0.05, 0.25, 0.5, 0.75, 0.95, 0.995]
OPTIONS = {"D0": None, "D2": "loglik:r600/no-offset", "D3": "loglik:both/no-offset", "D4": "loglik:both/startup-offset"}
OPTION_NAMES = {"D0": "00:19 Held Out (D0')", "D2": "R600 BTO + BFO (D2)", "D3": "both BFOs as recorded (D3, Holland H2 data)",
                "D4": "both BFOs, shared start-up offset (D4, Holland H1 data)"}
PS = [0.0, 0.5, 1.0]
STRATA = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
CANON = {"free": 0, "repro-radar": 1, "descent-climb": 2, "routes": 3, "waypoints": 4}
FAMS = {1: "A1", 2: "A2", 3: "B", 6: "outside B"}
PAD_PRE_S, PAD_POST_S, ROUND_S, CONV_S, ESS_MIN = 600.0, 1200.0, 300.0, 300.0, 1000.0
OHASISBIO = {  # research-radar-infrasound-ohasisbio.md (Royer LDO-201608 Table 1); SWAMS = SWAMS-2
    "NEAMS": (-(31 + 34.12 / 60), 83 + 11.36 / 60), "SWAMS": (-(42 + 58.53 / 60), 74 + 31.49 / 60),
    "SSEIR": (-(33 + 30.98 / 60), 70 + 52.57 / 60), "MAD": (-(26 + 4.99 / 60), 58 + 8.40 / 60),
    "WKER": (-(46 + 37.07 / 60), 60 + 34.20 / 60), "NCRO": (-(41 + 14.93 / 60), 53 + 5.05 / 60)}
RX_ORDER = ["H01W", "H08S", "H08N", "3315", "3376", "3274", "3275", "3250", "NEAMS", "SWAMS", "SSEIR", "MAD", "WKER", "NCRO"]
RX_LABEL = {"H01W": "Cape Leeuwin H01W", "H08S": "Diego Garcia South H08S", "H08N": "Diego Garcia North H08N",
            "3315": "IMOS 3315 Perth Canyon", "3376": "IMOS 3376 Perth Canyon", "3274": "IMOS 3274 Portland",
            "3275": "IMOS 3275 Portland", "3250": "IMOS 3250 Scott Reef", "NEAMS": "OHASISBIO NEAMS", "SWAMS": "OHASISBIO SWAMS",
            "SSEIR": "OHASISBIO SSEIR", "MAD": "OHASISBIO MAD", "WKER": "OHASISBIO WKER", "NCRO": "OHASISBIO NCRO"}
LAT_EDGES = np.arange(-45.0, -14.99, 0.5)


def receivers():
    rx = {}
    rows = [r for r in csv.reader(open(MODULE / "data" / "stations.csv")) if r and not r[0].startswith("#")]
    hdr, rows = rows[0], rows[1:]
    for triad in ("H01W", "H08S", "H08N"):
        el = [dict(zip(hdr, r)) for r in rows if dict(zip(hdr, r))["triad"] == triad]
        rx[triad] = (float(np.mean([float(e["latitude_deg"]) for e in el])), float(np.mean([float(e["longitude_deg"]) for e in el])))
    req = json.loads((MODULE / "data" / "ocean_paths" / "request.json").read_text())
    for p in req["paths"]:
        lg = p["name"].split("-")[-1]
        if lg in ("3315", "3376", "3250", "3274", "3275") and lg not in rx:
            rx[lg] = (p["b"][1], p["b"][0])
    rx.update(OHASISBIO)
    return {k: rx[k] for k in RX_ORDER}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()


def stratum_index(name):
    import re
    return CANON[re.sub(r"^(?:next|run)-(?:[a-z]-)?", "", name)]


def geodesic_km(lat, lon, rlat, rlon):
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    _, _, d = g.inv(lon, lat, np.full_like(lon, rlon), np.full_like(lat, rlat))
    return d / 1000.0


def hist(t, w):
    i = np.floor((t - GRID0) / DT).astype(np.int64)
    ok = (i >= 0) & (i < NBIN) & np.isfinite(t)
    h = np.bincount(i[ok], weights=w[ok], minlength=NBIN).astype(np.float32)
    return h, float(w[~ok].sum())


def wquant(h, qs):
    cp = np.cumsum(h.astype(np.float64)); tot = cp[-1]
    if tot <= 0: return [float("nan")] * len(qs)
    cp /= tot
    idx = np.minimum(np.searchsorted(cp, qs, side="left"), NBIN - 1)
    return [float(GRID0 + (i + 0.5) * DT) for i in idx]


def ln_weights(g, logon, which):
    """Row ln-weights for option `which` under EoF's total q=1/3 (C2 silent) cell, survival factor applied."""
    from scipy.special import gammaln, gammaincc
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    t = g("unix_s"); fo = g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
        lag = logon["logon_unix_s"] - fo
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
        alive = np.where(t > T_M0019B, 0.0, -np.inf)
        powered_0115 = (t > T_LOI_0115) & (~np.isfinite(fo) | (fo > T_LOI_0115))
        unp = np.where(powered_0115, -np.inf, alive)
        c1 = lfe + unp
        q = gammaincc(logon["lag_shape"], np.maximum(t - fo, 0.0) / logon["lag_scale_s"])
        c2 = -np.log(W_S) + unp + np.where(np.isfinite(fo), np.log(q), 0.0)
        lc = np.logaddexp(np.log(P_C1) + c1, np.log(1 - P_C1) + c2)
        ld = 0.0 if OPTIONS[which] is None else np.where(np.isfinite(g(OPTIONS[which])), g(OPTIONS[which]), -np.inf)
    return lw + surv + ld + lc


def p_factor(g, p):
    drawn = g("latent:pushover_drawn") == 1; ts = g("latent:pushover_to_surface") == 1
    f = np.ones(len(drawn))
    f[drawn & ts] = 2 * p; f[drawn & ~ts] = 2 * (1 - p)
    return f


def load_seed(sd):
    cols = (sd / "COLUMNS.txt").read_text().split()
    X = np.load(sd / "impacts32.npy", mmap_mode="r"); ci = {c: i for i, c in enumerate(cols)}
    tmap = {"unix_s": "t_impact_s", "latent:realised_flameout_unix_s": "t_realised_flameout_s"}
    cache = {}
    def g(k):
        if k not in cache:
            if k in tmap: cache[k] = np.asarray(X[:, ci[tmap[k]]], dtype=np.float64) + T0
            else: cache[k] = np.asarray(X[:, ci[k]], dtype=np.float64)
        return cache[k]
    meta = json.loads((sd / "run.json").read_text())
    return g, meta, X.shape[0]


def series_for(t, d_km, c_sofar, c_agw, w, rx):
    out = {"impact": hist(t, w)}
    for r in rx:
        out[f"{r}/SOFAR"] = hist(t + d_km[r] / c_sofar, w)
        out[f"{r}/AGW"] = hist(t + d_km[r] / c_agw, w)
    return out


def do_seed(args):
    stratum, sd, out = args
    sd = pathlib.Path(sd); out = pathlib.Path(out)
    t0 = time.time()
    g, meta, n = load_seed(sd)
    k = int(sd.name.split("-")[1])
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    rng = np.random.default_rng([20261021, stratum_index(stratum), k])
    c_s = rng.normal(C_SOFAR, C_SOFAR_SD, n); c_a = rng.uniform(C_AGW[0], C_AGW[1], n)
    t = g("unix_s"); lat, lon = g("latitude_deg"), g("longitude_deg")
    rx = receivers(); d = {r: geodesic_km(lat, lon, *rx[r]) for r in rx}
    fam = g("family4_code")
    res = {"n": n, "stratum": stratum, "seed": k, "logon": logon, "run_sha": sha(sd / "impacts32.npy")}
    H = {}; sums = {}; quant = {}; latsum = {}; beyond = {}
    for opt in OPTIONS:
        lnw = ln_weights(g, logon, opt)
        base = np.exp(np.where(np.isfinite(lnw), lnw, -np.inf)); base[~np.isfinite(base)] = 0.0
        for p in PS:
            w = base * p_factor(g, p)
            key = f"{opt}/p{p:g}"
            S = series_for(t, d, c_s, c_a, w, rx)
            for name, (h, bey) in S.items():
                H[f"{key}/{name}"] = h; beyond[f"{key}/{name}"] = bey
            # Kish sums per family and total; latitude histogram; lon*w per lat bin (arc proxy)
            sums[key] = {"sum": float(w.sum()), "sum2": float((w * w).sum()),
                         "fam": {FAMS[c]: [float(w[fam == c].sum()), float((w[fam == c] ** 2).sum())] for c in FAMS}}
            li = np.clip(np.searchsorted(LAT_EDGES, lat) - 1, 0, len(LAT_EDGES) - 2)
            latsum[key] = {"w": np.bincount(li, weights=w, minlength=len(LAT_EDGES) - 1),
                           "wlon": np.bincount(li, weights=w * lon, minlength=len(LAT_EDGES) - 1)}
            quant[key] = {name: wquant(h, QS) for name, (h, _) in S.items()}
    np.savez_compressed(out / f"{stratum}" / f"seed-{k}.npz",
                        meta=json.dumps({"res": res, "sums": sums, "quant": quant, "beyond": beyond}),
                        keys=np.array(list(H.keys())), H=np.stack([H[kk] for kk in H]),
                        lat_keys=np.array(list(latsum.keys())),
                        lat_w=np.stack([latsum[kk]["w"] for kk in latsum]), lat_wlon=np.stack([latsum[kk]["wlon"] for kk in latsum]))
    return stratum, k, n, time.time() - t0


def do_supplement(supp, out):
    z = np.load(supp); j = json.loads(pathlib.Path(str(supp)[:-4] + ".json").read_text())
    tech = z["technique"]; sel = tech >= 1
    t = z["t_impact_s"][sel].astype(np.float64) + T0; lat = z["latitude_deg"][sel].astype(np.float64); lon = z["longitude_deg"][sel].astype(np.float64)
    fam = z["family4_code"][sel]; n = int(sel.sum())
    rng = np.random.default_rng([20261021, 9, 0])
    c_s = rng.normal(C_SOFAR, C_SOFAR_SD, n); c_a = rng.uniform(C_AGW[0], C_AGW[1], n)
    rx = receivers(); d = {r: geodesic_km(lat, lon, *rx[r]) for r in rx}
    H = {}; sums = {}; quant = {}; latsum = {}; beyond = {}; share = {}
    for opt in OPTIONS:
        lnw_all = z[f"lnw:comb/{opt}"].astype(np.float64)
        w_all = np.exp(lnw_all); w_all[~np.isfinite(w_all)] = 0.0
        share[opt] = {"supplement": float(w_all[sel].sum()), "production_in_file": float(w_all[~sel].sum()), "total": float(w_all.sum())}
        w = w_all[sel]
        for p in PS:   # native weights at every p (declared gap: no pushover_to_surface column)
            key = f"{opt}/p{p:g}"
            S = series_for(t, d, c_s, c_a, w, rx)
            for name, (h, bey) in S.items():
                H[f"{key}/{name}"] = h; beyond[f"{key}/{name}"] = bey
            sums[key] = {"sum": float(w.sum()), "sum2": float((w * w).sum()),
                         "fam": {FAMS[c]: [float(w[fam == c].sum()), float((w[fam == c] ** 2).sum())] for c in FAMS}}
            li = np.clip(np.searchsorted(LAT_EDGES, lat) - 1, 0, len(LAT_EDGES) - 2)
            latsum[key] = {"w": np.bincount(li, weights=w, minlength=len(LAT_EDGES) - 1), "wlon": np.bincount(li, weights=w * lon, minlength=len(LAT_EDGES) - 1)}
            quant[key] = {name: wquant(h, QS) for name, (h, _) in S.items()}
    np.savez_compressed(pathlib.Path(out) / "supplement.npz",
                        meta=json.dumps({"res": {"n": n, "rows_in_file": int(len(tech)), "json": j, "sha": sha(supp)}, "sums": sums, "quant": quant,
                                         "beyond": beyond, "share": share}),
                        keys=np.array(list(H.keys())), H=np.stack([H[kk] for kk in H]),
                        lat_keys=np.array(list(latsum.keys())), lat_w=np.stack([latsum[kk]["w"] for kk in latsum]), lat_wlon=np.stack([latsum[kk]["wlon"] for kk in latsum]))
    return n, share


def hms(ts):
    if not np.isfinite(ts): return "nan"
    s = int(round(ts - T0)); d = 0
    while s < 0: s += 86400; d -= 1
    while s >= 86400: s -= 86400; d += 1
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}" + ("" if d == 0 else f"({d:+d}d)")


def held_intervals():
    """Recording intervals the module holds, per receiver, as (start_unix, end_unix)."""
    iv = {r: [] for r in RX_ORDER}
    import datetime as dt
    for r in csv.DictReader(open(MODULE / "data" / "imos" / "recordings.csv")):
        s = dt.datetime.fromisoformat(r["start_logger"]).timestamp()
        iv[r["logger"]].append((s, s + float(r["dur_s"])))
    iv["H01W"] = [(T0 + 27 * 60, T0 + 57 * 60)]                 # Kadri 2024 Fig. 9 panels a, b, c (digitised traces)
    iv["H08S"] = [(T0 + 60 * 60, T0 + 80 * 60)]                 # panels d, e
    return iv


def coverage_fraction(h, intervals):
    tot = float(h.sum())
    if tot <= 0: return float("nan")
    e = GRID0 + np.arange(NBIN + 1) * DT; m = np.zeros(NBIN)
    for a, b in intervals:
        lo = np.clip(e[:-1], a, b); hi = np.clip(e[1:], a, b); m += np.maximum(hi - lo, 0) / DT
    return float((h.astype(np.float64) * m).sum() / tot)


def pool(eof, out, repo_out, strata):
    out = pathlib.Path(out); repo_out = pathlib.Path(repo_out); repo_out.mkdir(parents=True, exist_ok=True)
    fe = json.loads((pathlib.Path(eof) / "summary" / "family-evidence-run-j.json").read_text()); p_core = fe["p_core"]
    supp = np.load(out / "supplement.npz"); sm = json.loads(str(supp["meta"])); skeys = list(supp["keys"]); sH = supp["H"]
    keys = None; acc = {}; acc_lat = {}; sums = {}; per_seed_q = {}; beyond = {}; seeds_used = {}; nrows = 0; shas = {}
    for s in strata:
        files = sorted((out / s).glob("seed-*.npz"), key=lambda p: int(p.stem.split("-")[1])); K = len(files); seeds_used[s] = K
        for f in files:
            z = np.load(f); m = json.loads(str(z["meta"])); nrows += m["res"]["n"]; shas[f"{s}/{f.stem}"] = m["res"]["run_sha"]
            if keys is None: keys = list(z["keys"]); lat_keys = list(z["lat_keys"])
            assert list(z["keys"]) == keys
            c = p_core[s] / K
            H = z["H"].astype(np.float64) * c
            for i, kk in enumerate(keys): acc[kk] = acc.get(kk, 0) + H[i]
            for i, kk in enumerate(lat_keys):
                a = acc_lat.setdefault(kk, {"w": 0, "wlon": 0}); a["w"] = a["w"] + z["lat_w"][i] * c; a["wlon"] = a["wlon"] + z["lat_wlon"][i] * c
            for kk, v in m["sums"].items():
                a = sums.setdefault(kk, {"sum": 0.0, "sum2": 0.0, "fam": {}, "strata": {}})
                a["sum"] += c * v["sum"]; a["sum2"] += c * c * v["sum2"]
                st = a["strata"].setdefault(s, {"sum": 0.0, "sum2": 0.0}); st["sum"] += c * v["sum"]; st["sum2"] += c * c * v["sum2"]
                for fn, (s1, s2) in v["fam"].items():
                    fa = a["fam"].setdefault(fn, [0.0, 0.0]); fa[0] += c * s1; fa[1] += c * c * s2
            for kk, v in m["beyond"].items(): beyond[kk] = beyond.get(kk, 0.0) + c * v
            for kk, v in m["quant"].items():
                for name, qv in v.items(): per_seed_q.setdefault(f"{kk}/{name}", {}).setdefault(s, []).append(qv)
    # supplement mixing
    pooled = {}; ess = {}; share_rows = []
    for kk in keys:
        opt = kk.split("/")[0]; key2 = "/".join(kk.split("/")[:2])
        Zs = sums[key2]["sum"]; sD = sm["share"][opt]["supplement"]
        Fs = acc[kk] / Zs if Zs > 0 else acc[kk]
        hs = sH[skeys.index(kk)].astype(np.float64); Zsup = sm["sums"][key2]["sum"]; Fsup = hs / Zsup if Zsup > 0 else hs
        pooled[kk] = (1 - sD) * Fs + sD * Fsup
    for key2, v in sums.items():
        opt = key2.split("/")[0]; sD = sm["share"][opt]["supplement"]; Zs = v["sum"]; Zsup = sm["sums"][key2]["sum"]
        # Kish ESS of the mixture: weights scaled so strata carry (1 - sD) and the supplement sD
        a = (1 - sD) / Zs if Zs > 0 else 0; b = sD / Zsup if Zsup > 0 else 0
        S1 = (1 - sD) + sD; S2 = a * a * v["sum2"] + b * b * sm["sums"][key2]["sum2"]
        fam = {}
        for fn in FAMS.values():
            f1 = a * v["fam"].get(fn, [0, 0])[0] + b * sm["sums"][key2]["fam"].get(fn, [0, 0])[0]
            f2 = a * a * v["fam"].get(fn, [0, 0])[1] + b * b * sm["sums"][key2]["fam"].get(fn, [0, 0])[1]
            fam[fn] = {"share": f1 / S1, "ess": (f1 * f1 / f2) if f2 > 0 else 0.0}
        strata_share = {s: (1 - sD) * st["sum"] / Zs for s, st in v["strata"].items()}
        strata_ess = {s: (st["sum"] ** 2 / st["sum2"]) if st["sum2"] > 0 else 0.0 for s, st in v["strata"].items()}
        ess[key2] = {"ess": S1 * S1 / S2 if S2 > 0 else 0.0, "ess_strata_only": Zs * Zs / v["sum2"] if v["sum2"] > 0 else 0.0,
                     "ess_supplement": (Zsup ** 2 / sm["sums"][key2]["sum2"]) if sm["sums"][key2]["sum2"] > 0 else 0.0,
                     "supplement_share": sD, "family": fam, "strata_share": strata_share, "strata_ess": strata_ess,
                     "ln_Zhat_strata": float(np.log(Zs)) if Zs > 0 else None}
    rx = receivers(); iv = held_intervals()
    rows = []; cov = []
    for opt in OPTIONS:
        for p in PS:
            key2 = f"{opt}/p{p:g}"
            qi = wquant(pooled[f"{key2}/impact"], QS)
            lat99 = None
            lw_ = acc_lat[key2]["w"]; cl = np.cumsum(lw_) / lw_.sum() if lw_.sum() > 0 else None
            if cl is not None: lat99 = float(LAT_EDGES[min(np.searchsorted(cl, 0.99), len(LAT_EDGES) - 2) + 1])
            rows.append(dict(receiver="impact", receiver_label="impact time", option=opt, option_name=OPTION_NAMES[opt], p=p, branch="-",
                             **{f"q{q * 100:g}": hms(v) for q, v in zip(QS, qi)}, **{f"q{q * 100:g}_unix": v for q, v in zip(QS, qi)},
                             window_start="", window_end="", unconverged="", **{"seed_spread_q0.5_s": "", "seed_spread_q99.5_s": ""},
                             ess=ess[key2]["ess"], supplement_share=ess[key2]["supplement_share"], lat99_north_deg=lat99,
                             mass_beyond_grid=beyond.get(f"{key2}/impact", 0.0) / sums[key2]["sum"] if sums[key2]["sum"] > 0 else None))
            for r in RX_ORDER:
                for br in ("SOFAR", "AGW"):
                    kk = f"{key2}/{r}/{br}"; q = wquant(pooled[kk], QS)
                    psq = per_seed_q.get(kk, {}).get("run-j-waypoints", [])
                    sp0 = max(x[0] for x in psq) - min(x[0] for x in psq) if psq else float("nan")
                    sp1 = max(x[-1] for x in psq) - min(x[-1] for x in psq) if psq else float("nan")
                    unconv = bool(np.isfinite(sp0) and (sp0 > CONV_S or sp1 > CONV_S))
                    lo, hi = q[0], q[-1]
                    if unconv:
                        lo = min(lo, min(x[0] for x in psq)); hi = max(hi, max(x[-1] for x in psq))
                    ws = np.floor((lo - PAD_PRE_S - T0) / ROUND_S) * ROUND_S + T0; we = np.ceil((hi + PAD_POST_S - T0) / ROUND_S) * ROUND_S + T0
                    rows.append(dict(receiver=r, receiver_label=RX_LABEL[r], option=opt, option_name=OPTION_NAMES[opt], p=p, branch=br,
                                     **{f"q{qq * 100:g}": hms(v) for qq, v in zip(QS, q)}, **{f"q{qq * 100:g}_unix": v for qq, v in zip(QS, q)},
                                     window_start=hms(ws), window_end=hms(we), unconverged=int(unconv), **{"seed_spread_q0.5_s": sp0, "seed_spread_q99.5_s": sp1},
                                     ess=ess[key2]["ess"], supplement_share=ess[key2]["supplement_share"], lat99_north_deg=lat99,
                                     mass_beyond_grid=beyond.get(kk, 0.0) / sums[key2]["sum"] if sums[key2]["sum"] > 0 else None))
                    held = iv.get(r, [])
                    cov.append(dict(receiver=r, receiver_label=RX_LABEL[r], option=opt, p=p, branch=br,
                                    held_fraction=coverage_fraction(pooled[kk], held) if held else 0.0,
                                    n_held_records=len(held), held_seconds=sum(b - a for a, b in held),
                                    held_source=("IMOS 307 s records (data/imos/recordings.csv)" if r.isdigit() else
                                                 "Kadri 2024 Fig. 9 panels a-c, digitised" if r == "H01W" else
                                                 "Kadri 2024 Fig. 9 panels d-e, digitised" if r == "H08S" else "nothing held")))
    # recommended request windows: union over options with ESS >= 1000, per receiver, branch, p
    req = []
    for p in PS:
        for r in RX_ORDER:
            for br in ("SOFAR", "AGW"):
                sel = [x for x in rows if x["receiver"] == r and x["branch"] == br and x["p"] == p and x["ess"] >= ESS_MIN]
                if not sel: req.append(dict(receiver=r, branch=br, p=p, start="", end="", options="", note="no option with ESS >= 1000")); continue
                st = min(x["q0.5_unix"] for x in sel); en = max(x["q99.5_unix"] for x in sel)
                ws = np.floor((st - PAD_PRE_S - T0) / ROUND_S) * ROUND_S + T0; we = np.ceil((en + PAD_POST_S - T0) / ROUND_S) * ROUND_S + T0
                req.append(dict(receiver=r, branch=br, p=p, start=hms(ws), end=hms(we), start_unix=ws, end_unix=we, options=" ".join(sorted({x["option"] for x in sel})),
                                note="UNCONVERGED tail widened" if any(x["unconverged"] for x in sel) else ""))
    def wcsv(path, rws):
        with open(path, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rws[0].keys())); wr.writeheader(); wr.writerows(rws)
    for d in (out, repo_out):
        wcsv(d / "windows.csv", rows); wcsv(d / "coverage.csv", cov); wcsv(d / "request_windows.csv", req)
        (d / "ess.json").write_text(json.dumps(ess, indent=1))
    arc = {}
    for kk, a in acc_lat.items():
        w_ = a["w"]; arc[kk] = {"lat_mid": (0.5 * (LAT_EDGES[:-1] + LAT_EDGES[1:])).tolist(), "w": w_.tolist(),
                               "lon_mean": np.where(w_ > 0, a["wlon"] / np.where(w_ > 0, w_, 1), np.nan).tolist()}
    np.savez_compressed(out / "pooled.npz", keys=np.array(keys), H=np.stack([pooled[k] for k in keys]).astype(np.float32), arc=json.dumps(arc))
    (repo_out / "arc_lat_lon.json").write_text(json.dumps({k: arc[k] for k in arc if k.startswith("D0/p0.5")}, indent=0))
    run = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "script": "prepare/run_j_windows.py", "eof_root": str(eof), "rows": nrows,
           "seeds_used": seeds_used, "p_core": p_core, "supplement": {"rows_used": sm["res"]["n"], "rows_in_file": sm["res"]["rows_in_file"], "sha256": sm["res"]["sha"], "share": sm["share"]},
           "grid": {"start_unix": GRID0, "end_unix": GRID1, "dt_s": DT}, "options": OPTION_NAMES, "p": PS, "arrival_model": {"sofar_c_kms": [C_SOFAR, C_SOFAR_SD], "agw_c_kms": list(C_AGW)},
           "weights": "EoF total q=1/3 (C2 silent), survival factor, p_core x Zhat pooling by evidence; p re-weighting by push-over flags (module rule)",
           "labels": ["PREDICTIVE, NOT CALIBRATED", "caveat C1 propagation slope misfit", "caveat C2 coupling efficiency not calibrated", "AGW speed assumed U(1.40,1.50) km/s, not modelled",
                      "supplement rows keep native p=0.5 weights at every p (gap)", "run J convergence accepted as a pass by project ruling, 16 Oct 2026"],
           "impacts32_sha256": shas, "receivers": rx}
    for d in (out, repo_out): (d / "run.json").write_text(json.dumps(run, indent=1))
    return rows, cov, ess


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["seeds", "supplement", "pool"])
    ap.add_argument("--eof"); ap.add_argument("--out"); ap.add_argument("--supp"); ap.add_argument("--repo-out")
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--strata", nargs="*", default=STRATA); ap.add_argument("--seeds", nargs="*")
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.mode == "seeds":
        tasks = []
        for s in a.strata:
            (out / s).mkdir(exist_ok=True)
            for sd in sorted((pathlib.Path(a.eof) / s).glob("seed-*")):
                if not (sd / "impacts32.npy").exists(): continue
                if a.seeds and sd.name.split("-")[1] not in a.seeds: continue
                if (out / s / f"{sd.name}.npz").exists(): continue
                tasks.append((s, str(sd), str(out)))
        print(f"tasks {len(tasks)} workers {a.workers}", flush=True)
        with ProcessPoolExecutor(a.workers) as ex:
            for s, k, n, dt in ex.map(do_seed, tasks):
                print(f"done {s}/seed-{k} rows {n} {dt:.0f}s", flush=True)
    elif a.mode == "supplement":
        n, share = do_supplement(a.supp, out); print("supplement rows", n, json.dumps(share))
    else:
        rows, cov, ess = pool(a.eof, out, a.repo_out, a.strata)
        for r in rows:
            if r["p"] == 0.5 and r["branch"] in ("SOFAR", "-") and r["option"] == "D0":
                print(r["receiver"], r["q0.5"], r["q5"], r["q50"], r["q95"], r["q99.5"], r["window_start"], r["window_end"], "unconv" if r["unconverged"] else "", f"ESS {r['ess']:.0f}")


if __name__ == "__main__":
    main()
