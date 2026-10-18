"""Scan run J impact rows for the Kadri/Haixun locality L (hydroacoustic leg, 18 Oct 2026).
Per seed: per-row log-weight components exactly as option_table_0019.seed_terms (end-of-flight branch 5d060f0),
normalisers over ALL rows for the six headline cells 'D{d} total q=0.333 (C2 silent)', and the rows inside a
superset of L (bearing 306.18 +/- 1.5 deg from H01W at 1,400-1,950 km, or within 400 km of the arc crossing or Haixun).
Usage: python scan_runj_L.py EOF_ROOT CORE_ROOT SMOKE_DIR OUT_DIR stratum [seed ...]"""
import sys, json, pathlib, csv, time
import numpy as np
EOF_ROOT, CORE_ROOT, SMOKE, OUT = (pathlib.Path(a) for a in sys.argv[1:5]); ST = sys.argv[5]
sys.path.insert(0, str(SMOKE))
from scipy.special import logsumexp, gammaln
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor, SATCOM_CSV
import option_table_0019 as OT
from pyproj import Geod
G = Geod(ellps="WGS84"); H01W = (-34.8903, 114.1426); XING = (-25.732, 101.369); HX = (-25.975, 101.461)
P_CORE = {"run-j-waypoints": 0.9982, "run-j-free": 0.0013, "run-j-repro-radar": 0.0003, "run-j-descent-climb": 0.0002}
seeds = sys.argv[6:] or sorted(p.name for p in (EOF_ROOT / ST).glob("seed-*") if p.is_dir())
K = len([p for p in (EOF_ROOT / ST).glob("seed-*") if p.is_dir()])
OUT.mkdir(parents=True, exist_ok=True)
for sn in seeds:
    t0 = time.time(); sd = EOF_ROOT / ST / sn; o = OUT / f"{ST}__{sn}.npz"
    if o.exists(): continue
    meta, g = load(sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    obs = {r["epoch_id"]: r for r in csv.DictReader(open(SATCOM_CSV))}
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(CORE_ROOT / ST / "bto-bfo" / sn / "handoff-m0011" / "handoff.npy", mmap_mode="r")[:, 9])[g("parent").astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": der["r600-bto"], "D2": col("r600/no-offset"), "D3": col("both/no-offset"),
         "D4": col("both/startup-offset"), "D5": OT.d5_loglik(g, V, obs)}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    C2s = -np.log(OT.W_S) + constraint_log_factor(g, logon, "other", "silent")
    C2u = -np.log(OT.W_S) + constraint_log_factor(g, logon, "other", "unpowered")
    p = 0.75; mix = np.logaddexp(np.log(p) + C1, np.log(1 - p) + C2s)
    base = lw + surv; c = np.log(P_CORE[ST] / K)
    norms = {d: float(logsumexp((base + ld + mix)[np.isfinite(base + ld + mix)])) if np.isfinite(base + ld + mix).any() else -np.inf for d, ld in D.items()}
    lat, lon = g("latitude_deg"), g("longitude_deg")
    az, _, dist = G.inv(np.full(lat.shape, H01W[1]), np.full(lat.shape, H01W[0]), lon, lat); az = az % 360; dist = dist / 1e3
    _, _, dx = G.inv(np.full(lat.shape, XING[1]), np.full(lat.shape, XING[0]), lon, lat)
    _, _, dh = G.inv(np.full(lat.shape, HX[1]), np.full(lat.shape, HX[0]), lon, lat)
    sel = ((np.abs(az - 306.18) <= 1.5) & (dist >= 1400) & (dist <= 1950)) | (dx <= 400e3) | (dh <= 400e3)
    idx = np.nonzero(sel)[0]
    z = np.load(sd / "tau90_v1.npz")
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    keep = dict(row=idx, lat=lat[idx], lon=lon[idx], az=az[idx], dist_km=dist[idx], dx_km=dx[idx] / 1e3, dh_km=dh[idx] / 1e3,
                t_impact=g("t_impact_s")[idx], ke=g("kinetic_energy_j")[idx], vke=g("vertical_kinetic_energy_j")[idx],
                e_tr=np.asarray(z["energy_transferred_j"], float)[idx], tau90=np.asarray(z["tau90_s"], float)[idx],
                fpa=g("flight_path_angle_deg")[idx], vup=g("velocity_up_mps")[idx], mass=g("mass_kg")[idx],
                vh=np.hypot(g("velocity_east_mps"), g("velocity_north_mps"))[idx], fam4=np.asarray(f4)[idx],
                base=base[idx], C1=C1[idx], C2s=C2s[idx], C2u=C2u[idx], c_stratum=np.array(c),
                pushover=g("latent:pushover_drawn")[idx], t_flameout=g("latent:realised_flameout_unix_s")[idx],
                parent=g("parent")[idx])
    for d, ld in D.items(): keep["ld_" + d] = ld[idx]
    keep["norms_json"] = np.array(json.dumps(norms)); keep["n_rows"] = np.array(len(w))
    keep = {k: (v.astype(np.float32) if (isinstance(v, np.ndarray) and v.dtype == np.float64 and v.ndim == 1 and k not in ('t_impact', 't_flameout', 'base', 'C1', 'C2s', 'C2u') and not k.startswith('ld_')) else v) for k, v in keep.items()}
    np.savez_compressed(o, **keep)
    print(f"{ST}/{sn}: rows {len(w)} kept {len(idx)} {time.time()-t0:.0f}s", flush=True)
