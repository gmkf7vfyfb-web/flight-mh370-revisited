"""Per-impact terms shared by the truth draw and the scoring (production definitions, smoke/option_table_0019.py and
smoke/displacement_hist.py at 16f2eb1): D0-D5 x log-on cause, survival, families; plus the smoke's reduced drift and search terms."""
import json, csv, math, pathlib
import numpy as np
from scipy.special import gammaln, logsumexp
from scipy.stats import norm
from compact_impacts import open_seed, family_labels
from displacement_hist import constraint_log_factor

W_S = 1394241356.0 - 1394237458.0
Q = 1.0 / 3.0; P1 = 1.0 / (1.0 + Q)
FAMNAME = {1.0: "A1", 2.0: "A2", 3.0: "B", 6.0: "B"}


def obs_sd(obs_csv):
    O = {r["epoch_id"]: r for r in csv.DictReader(open(obs_csv))}
    return {e: (float(O[e]["bto_sd_us"]), float(O[e]["bfo_sd_hz"])) for e in ("m0019a", "m0019b")}


def terms(run, sd, handoff_npy, obs_csv):
    """dict of per-row arrays: lw (within-seed log weight), surv, D0..D5 log-likelihoods, log C1 / C2-silent terms, family,
    impact lat/lon/time, cross-arc distance, parent. Same algebra as option_table_0019.seed_terms (D5 with the SD of obs_csv)."""
    meta, g = open_seed(run, sd); logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    s = obs_sd(obs_csv); w = g("weight"); lw = np.log(w) - np.log(w.sum())
    par = g("parent").astype(np.int64); V = np.asarray(np.load(handoff_npy, mmap_mode="r")[:, 9])[par]
    col = lambda k: np.where(np.isfinite(g("loglik:" + k)), g("loglik:" + k), -np.inf)
    r = g("bto_residual_us:m0019a"); i1 = g("bfo_innovation_hz:m0019a"); i2 = g("bfo_innovation_hz:m0019b")
    s_bto, s1, s2 = s["m0019a"][0], s["m0019a"][1], s["m0019b"][1]
    bto = np.where(np.isfinite(r), -0.5 * ((r / s_bto) ** 2 + np.log(2 * np.pi * s_bto ** 2)), -np.inf)
    S1 = V + s1 ** 2; K = V / S1; S2 = V * (1 - K) + s2 ** 2; m = i2 - K * i1; sdv = np.sqrt(S2); lo, hi = 17.0, 130.0
    with np.errstate(divide="ignore", invalid="ignore"):
        band = np.log(np.clip(norm.cdf((m - lo) / sdv) - norm.cdf((m - hi) / sdv), 1e-300, None)) - np.log(hi - lo)
    d5 = np.where(np.isfinite(r) & np.isfinite(i1) & np.isfinite(i2), bto + norm.logpdf(i1, 0, np.sqrt(S1)) + band, -np.inf)
    D = {"D0": np.zeros(len(w)), "D1": bto, "D2": col("r600/no-offset"), "D3": col("both/no-offset"), "D4": col("both/startup-offset"), "D5": d5}
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
        surv = np.log1p(-np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    c1 = np.log(P1) + lfe + constraint_log_factor(g, logon, "fuel-exhaustion", "unpowered")
    c2 = np.log(1 - P1) - np.log(W_S) + constraint_log_factor(g, logon, "other", "silent")
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    return dict(lw=lw, surv=surv, D=D, c1=c1, c2=c2, fam=f4, lat=g("latitude_deg"), lon=g("longitude_deg"), t=g("unix_s"),
                xarc=g("arc_distance_nm"), parent=par, i1=i1, i2=i2, r600=r, r1200=g("bto_residual_us:m0019b"), meta=meta)


# ---------- reduced search term (V1 central, re-implemented from results/searched-areas-spatial-detection/README.md) ----------
class Search:
    def __init__(self, npz):
        z = np.load(npz); self.s, self.w, self.st = float(z["south"]), float(z["west"]), float(z["step"])
        f = z["f_fig"]; c = z["p2"]; q = 0.95 * (1 - f) + 0.70 * f
        rho = np.minimum(0.05 * z["w_rho"], 0.95)
        miss = (1 - np.nan_to_num(c) * np.nan_to_num(q)) * (1 - 0.9 * np.nan_to_num(z["oi2018"])) * (1 - 0.9 * np.nan_to_num(z["oi2025"]))
        searched = (np.nan_to_num(c) > 0) | (np.nan_to_num(z["oi2018"]) > 0) | (np.nan_to_num(z["oi2025"]) > 0)
        rho = np.where(searched, np.nan_to_num(rho, nan=0.05), 0.0)
        self.pnf = (rho + (1 - rho) * miss).astype(np.float64)       # P(no find | wreck in cell)
        self.shape = self.pnf.shape

    def p_no_find(self, lat, lon):
        i = np.floor((np.asarray(lat) - self.s) / self.st).astype(np.int64); j = np.floor((np.asarray(lon) - self.w) / self.st).astype(np.int64)
        inside = (i >= 0) & (i < self.shape[0]) & (j >= 0) & (j < self.shape[1])
        out = np.ones(np.shape(lat)); out[inside] = self.pnf[i[inside], j[inside]]
        return out


# ---------- reduced drift term (segment level, from the drift module's own arc-latitude node outputs) ----------
class Drift:
    def __init__(self, node_files, audit_csv):
        A = {r["object_id"]: r for r in csv.DictReader(open(audit_csv))}
        self.models = {}
        for model, files in node_files.items():
            rows = []
            for f in files:
                rows += list(csv.DictReader(open(f)))
            hdr = list(rows[0].keys())
            items = [h[len("n_eff_debris_"):] for h in hdr if h.startswith("n_eff_debris_")]
            classes = sorted({h.split("_")[1] if False else None for h in []})
            cls = {}
            for it in items:
                a = A.get(it)
                cls[it] = a["motion_class"] if a else None
            seg = sorted({int(h.rsplit("_", 1)[1]) for h in hdr if h.startswith("p_flaperon_") and h.rsplit("_", 1)[1].isdigit()})
            lat = np.array([float(r["lat_deg"]) for r in rows]); lon = np.array([float(r["lon_deg"]) for r in rows])
            P = {}
            for c in ("flaperon", "low_exposure_exterior", "high_windage_interior"):
                P[c] = np.array([[float(r[f"p_{c}_{s}"]) for s in seg] for r in rows])
            o = np.argsort(lat)
            self.models[model] = dict(lat=lat[o], lon=lon[o], P={c: v[o] for c, v in P.items()})
        self.items = [(it, cls[it]) for it in items if cls[it] in ("flaperon", "low_exposure_exterior", "high_windage_interior")]
        self.items_dropped = [it for it in items if cls[it] not in ("flaperon", "low_exposure_exterior", "high_windage_interior")]
        self.nseg = len(seg)

    def node(self, model, lat):
        L = self.models[model]["lat"]; j = np.clip(np.searchsorted(L, lat), 1, len(L) - 1)
        j = np.where(np.abs(L[j - 1] - lat) < np.abs(L[j] - lat), j - 1, j)
        inside = (lat >= L[0] - 0.5) & (lat <= L[-1] + 0.5)
        return j, inside

    def simulate(self, model, lat, rng):
        j, inside = self.node(model, np.array([lat])); j = int(j[0])
        out = []
        for it, c in self.items:
            p = self.models[model]["P"][c][j]; pr = np.append(p, max(0.0, 1 - p.sum())); pr /= pr.sum()
            out.append(int(rng.choice(len(pr), p=pr)))            # segment index, or nseg = not found in any segment
        return out, bool(inside[0])

    def loglik(self, outcomes, lat):
        res = {}
        for model, M in self.models.items():
            j, inside = self.node(model, lat); ll = np.zeros(len(lat))
            for (it, c), o in zip(self.items, outcomes):
                p = M["P"][c][j]
                po = p[:, o] if o < self.nseg else np.clip(1 - p.sum(1), 0, 1)
                ll += np.log(np.clip(po, 1e-12, None))             # smoke floor; declared (composition rule 4 forbids floors in production)
            res[model] = np.where(inside, ll, np.nan)
        a = np.vstack([res[m] for m in self.models]); return np.log(np.mean(np.exp(a - np.nanmax(a, 0)), 0)) + np.nanmax(a, 0), res
