"""Block 11 worker: one run J seed (or the northern supplement) -> five float32 columns row-aligned with impacts32.npy,
streamed statistics (prereg.py section 9) and a 1-in-125 subsample. Single-threaded; launched by driver.py.
Usage: python worker.py <stratum> <seed> <staging_dir>     |     python worker.py supplement 0 <staging_dir>
Column rule: NaN = not computed (non-finite inputs), 0.0 = computed with no information (no scored window at any receiver).
"""
from __future__ import annotations
import hashlib, json, os, shutil, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
import run_j_windows as W
from common import Machinery

NB1 = len(R.LAT_BAND_EDGES_1DEG) + 1          # 21 bands + 2 overflow = 23 bins (index 0 south, 22 north)
NBH = len(R.LAT_BIN_EDGES_HALF) - 1           # 60 half-degree bins
FAM_CODES = (1, 2, 3, 6)
KEYS = [f"{o}/p{p:g}" for o in R.OPTIONS for p in R.PS]


def free_gib(path):
    st = os.statvfs(path); return st.f_bavail * st.f_frsize / 2 ** 30


def band1(lat):
    return np.clip(np.searchsorted(R.LAT_BAND_EDGES_1DEG, lat, side="right"), 0, NB1 - 1)


def binh(lat):
    return np.clip(np.searchsorted(R.LAT_BIN_EDGES_HALF, lat, side="right") - 1, 0, NBH - 1)


class Acc:
    """Streamed sums per option/p. eta axis = the 41 prior grid points (+3 fixed) of Machinery.eta_eval."""
    def __init__(self, K):
        z = lambda *s: np.zeros(s)
        self.n_rows = 0; self.n_ok = 0; self.n_scored_any = 0; self.n_E_fallback = 0; self.n_scored_rx = {rx: 0 for rx in R.RECEIVERS}
        self.sum_w = z(12, NB1); self.sum_w2 = z(12, NB1)
        self.fam_w = z(12, 4); self.fam_w2 = z(12, 4); self.fam_wL = z(12, 4); self.fam_wLims = z(12, 4)
        self.wPnd = {a: z(12, NB1, K) for a in R.ALPHAS}; self.wL = {a: z(12, NB1, K) for a in R.ALPHAS}
        self.wPnd_ims = {a: z(12, NB1, K) for a in R.ALPHAS}; self.wL_ims = {a: z(12, NB1, K) for a in R.ALPHAS}
        self.half_w = z(12, NBH); self.half_wL = {a: z(12, NBH) for a in R.ALPHAS}; self.half_wLims = {a: z(12, NBH) for a in R.ALPHAS}
        self.half_wlon = z(12, NBH)
        self.wLmarg = {a: z(12) for a in R.ALPHAS}; self.wLmarg_ims = {a: z(12) for a in R.ALPHAS}
        self.wLfixed = z(12, 3); self.wLfixed_ims = z(12, 3)
        self.wL_A = {a: z(12, NB1, K) for a in R.ALPHAS}; self.half_wLA = {a: z(12, NBH) for a in R.ALPHAS}; self.wLmarg_A = {a: z(12) for a in R.ALPHAS}; self.fam_wLA = z(12, 4)
        self.lnL_hist_edges = np.arange(-20.0, 20.01, 0.25); self.lnL_hist = z(12, len(self.lnL_hist_edges) - 1)

    def add(self, Wt, lat, lon, fam, lnL, lnPnd, lnL_ims, lnPnd_ims, M, mask, lnL_A=None):
        """Wt: [12, n] weights; lnL*: dict alpha -> [n, K]; mask: rows computed."""
        b1 = band1(lat); bh = binh(lat); fi = np.full(len(lat), -1)
        for k, c in enumerate(FAM_CODES): fi[fam == c] = k
        for a in R.ALPHAS:
            L = np.exp(np.clip(lnL[a], -700, 700)); P = np.exp(lnPnd[a]); Li = np.exp(np.clip(lnL_ims[a], -700, 700)); Pi = np.exp(lnPnd_ims[a])
            lm = M.marg(lnL[a]); lmi = M.marg(lnL_ims[a]); eLm = np.exp(np.clip(lm, -700, 700)); eLmi = np.exp(np.clip(lmi, -700, 700))
            if lnL_A is not None:
                LA = np.exp(np.clip(lnL_A[a], -700, 700)); eLmA = np.exp(np.clip(M.marg(lnL_A[a]), -700, 700))
            for j in range(12):
                w = Wt[j] * mask
                if lnL_A is not None:
                    self.wLmarg_A[a][j] += np.sum(w * eLmA); self.half_wLA[a][j] += np.bincount(bh, weights=w * eLmA, minlength=NBH)
                    if a == R.ALPHA_PRIMARY:
                        for k in range(4):
                            m = fi == k; self.fam_wLA[j, k] += np.sum(w[m] * eLmA[m])
                if a == R.ALPHA_PRIMARY:
                    for ff, name in enumerate(R.ETA_FIXED):
                        self.wLfixed[j, ff] += np.sum(w * np.exp(np.clip(M.fixed(lnL[a], name), -700, 700)))
                        self.wLfixed_ims[j, ff] += np.sum(w * np.exp(np.clip(M.fixed(lnL_ims[a], name), -700, 700)))
                    self.lnL_hist[j] += np.histogram(np.clip(lm, -19.99, 19.99), bins=self.lnL_hist_edges, weights=w)[0]
                    for k in range(4):
                        m = fi == k
                        self.fam_wL[j, k] += np.sum(w[m] * eLm[m]); self.fam_wLims[j, k] += np.sum(w[m] * eLmi[m])
                self.wLmarg[a][j] += np.sum(w * eLm); self.wLmarg_ims[a][j] += np.sum(w * eLmi)
                self.half_wL[a][j] += np.bincount(bh, weights=w * eLm, minlength=NBH); self.half_wLims[a][j] += np.bincount(bh, weights=w * eLmi, minlength=NBH)
                # vectorised band x eta sums
                Wb = np.zeros((NB1, len(lat))); Wb[b1, np.arange(len(lat))] = w
                self.wPnd[a][j] += Wb @ P; self.wL[a][j] += Wb @ L; self.wPnd_ims[a][j] += Wb @ Pi; self.wL_ims[a][j] += Wb @ Li
                if lnL_A is not None: self.wL_A[a][j] += Wb @ LA
        for j in range(12):
            w = Wt[j] * mask
            self.sum_w[j] += np.bincount(b1, weights=w, minlength=NB1); self.sum_w2[j] += np.bincount(b1, weights=w * w, minlength=NB1)
            self.half_w[j] += np.bincount(bh, weights=w, minlength=NBH); self.half_wlon[j] += np.bincount(bh, weights=w * lon, minlength=NBH)
            for k in range(4):
                m = fi == k; self.fam_w[j, k] += w[m].sum(); self.fam_w2[j, k] += (w[m] ** 2).sum()

    def dump(self, path, extra):
        d = dict(sum_w=self.sum_w, sum_w2=self.sum_w2, fam_w=self.fam_w, fam_w2=self.fam_w2, fam_wL=self.fam_wL, fam_wLims=self.fam_wLims,
                 half_w=self.half_w, half_wlon=self.half_wlon, wLfixed=self.wLfixed, wLfixed_ims=self.wLfixed_ims, lnL_hist=self.lnL_hist,
                 lnL_hist_edges=self.lnL_hist_edges)
        for a in R.ALPHAS:
            t = f"a{a:g}"
            d[f"wPnd_{t}"] = self.wPnd[a]; d[f"wL_{t}"] = self.wL[a]; d[f"wPnd_ims_{t}"] = self.wPnd_ims[a]; d[f"wL_ims_{t}"] = self.wL_ims[a]
            d[f"half_wL_{t}"] = self.half_wL[a]; d[f"half_wLims_{t}"] = self.half_wLims[a]; d[f"wLmarg_{t}"] = self.wLmarg[a]; d[f"wLmarg_ims_{t}"] = self.wLmarg_ims[a]
            d[f"wL_A_{t}"] = self.wL_A[a]; d[f"half_wLA_{t}"] = self.half_wLA[a]; d[f"wLmarg_A_{t}"] = self.wLmarg_A[a]
        d["fam_wLA"] = self.fam_wLA
        d["meta"] = json.dumps(dict(extra, n_rows=self.n_rows, n_ok=self.n_ok, n_scored_any=self.n_scored_any, n_E_fallback=self.n_E_fallback,
                                    n_scored_rx=self.n_scored_rx, keys=KEYS, eta_eval=list(map(float, extra.pop("eta_eval"))) if "eta_eval" in extra else None))
        np.savez_compressed(path, **d)


STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: RAM-grid IMOS TL, amplitude variant, statistics only
RAMGRID = STATS_ONLY or os.environ.get("B11_IMOS_RAMGRID") == "1"   # A4: column rewrite with the corrected IMOS table = B11_IMOS_RAMGRID=1 python driver.py


def run_seed(stratum, k, stg):
    M = Machinery(imos_ramgrid=RAMGRID); t0 = time.time()
    sd = R.RUN_J / stratum / f"seed-{k}"; g, meta, n = W.load_seed(sd); si = W.stratum_index(stratum)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    z = np.load(sd / "tau90_v1.npz"); assert int(z["method"]) == 1, "tau90 sidecar is not method 1"
    tau90 = np.asarray(z["tau90_s"], float)
    t = g("unix_s"); lat = g("latitude_deg"); lon = g("longitude_deg"); fam = g("family4_code")
    # E = contact kinetic energy: the tau90 sidecar's energy_transferred_j (impacts32's latent:impact_energy_transferred_j is NaN in
    # run J; amendment A1, plumbing only), then the impacts32 column, then 0.5 m v^2 (counted)
    E = np.asarray(z["energy_transferred_j"], float); E2 = g("latent:impact_energy_transferred_j"); E = np.where(np.isfinite(E), E, E2)
    Efb = 0.5 * g("mass_kg") * (g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    fb = ~np.isfinite(E) & np.isfinite(Efb); E = np.where(fb, Efb, E)
    ok = np.isfinite(t) & np.isfinite(lat) & np.isfinite(lon) & np.isfinite(E) & (E > 0) & np.isfinite(tau90) & (tau90 > 0)
    Lcal = np.random.default_rng([R.SEED, R.BLOCK, si, k]).normal(0.0, R.CAL_L_SD_DB, n)
    # weights per option / p (prereg 9): exp(ln_weights) * p_factor, zero where not finite or not computed
    Wt = np.zeros((12, n))
    for i, o in enumerate(R.OPTIONS):
        lnw = W.ln_weights(g, logon, o); base = np.exp(np.where(np.isfinite(lnw), lnw, -np.inf)); base[~np.isfinite(base)] = 0.0
        for j, p in enumerate(R.PS):
            Wt[3 * i + j] = base * W.p_factor(g, p) * ok
    A = Acc(len(M.eta_eval)); A.n_rows = n; A.n_ok = int(ok.sum()); A.n_E_fallback = int((fb & ok).sum())
    cols = {c: np.full(n, np.nan, np.float32) for c in R.COLUMNS}
    sub = {k_: [] for k_ in ("row", "lat", "lon", "t", "E", "tau", "fam", "Lcal", "lnL_grid", "lnL_grid_ims", "lnL_marg_imos", "lnL_marg_ims")}
    for s in range(0, n, R.CHUNK_ROWS):
        e = min(n, s + R.CHUNK_ROWS); sl = slice(s, e); m = ok[sl]; idx = np.arange(s, e)[m]
        if not m.any(): continue
        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau90[idx]); lnL_A = {} if STATS_ONLY else None
        for a in R.ALPHAS:
            if STATS_ONLY:
                l_g, p_g, nsc, l_a = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED, amp=True); lnL_A[a] = l_a
            else:
                l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY:
                A.n_scored_any += int((nsc + nsc_i > 0).sum())
                for rx in R.RECEIVERS: A.n_scored_rx[rx] += int(PP["sc"][rx].sum())
        ap = R.ALPHA_PRIMARY
        for name in R.ETA_FIXED:
            cols[f"hydro-lnL-imos-{name}"][idx] = M.fixed(lnL[ap], name).astype(np.float32)
        lm = M.marg(lnL[ap]); lmi = M.marg(lnL_ims[ap])
        cols["hydro-lnL-imos-margeta"][idx] = lm.astype(np.float32); cols["hydro-lnL-ims-proxy-margeta"][idx] = lmi.astype(np.float32)
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)), lnL_A)
        # subsample (1 in 125 of the seed's rows, by row index)
        ss = idx[(idx % R.SUBSAMPLE_EVERY) == 0]; pos = np.searchsorted(idx, ss)
        sub["row"].append(ss); sub["lat"].append(lat[ss]); sub["lon"].append(lon[ss]); sub["t"].append(t[ss]); sub["E"].append(E[ss]); sub["tau"].append(tau90[ss])
        sub["fam"].append(fam[ss]); sub["Lcal"].append(Lcal[ss]); sub["lnL_grid"].append(lnL[ap][pos].astype(np.float32)); sub["lnL_grid_ims"].append(lnL_ims[ap][pos].astype(np.float32))
        sub["lnL_marg_imos"].append(lm[pos]); sub["lnL_marg_ims"].append(lmi[pos])
        print(f"{stratum}/seed-{k}: rows {e}/{n} {time.time() - t0:.0f} s", flush=True)
    # per-seed checks before writing
    for c in R.COLUMNS:
        assert len(cols[c]) == n and np.all(np.isfinite(cols[c][ok])) and np.all(np.isnan(cols[c][~ok]))
    od = Path(stg) / stratum / f"seed-{k}"; od.mkdir(parents=True, exist_ok=True)
    gib = free_gib(stg); write = list(R.COLUMNS) if (gib >= R.DISK_FLOOR_GIB or os.environ.get("B11_TOPUP") == "1") else ["hydro-lnL-imos-margeta"]
    if STATS_ONLY: write = []      # amendment A4(b): no columns
    # B11_TOPUP=1: re-run of a seed that was short-written while another process held the disk below the floor (amendment A2)
    shas = []
    for c in write:
        f = od / f"{c}.npy"; np.save(f, cols[c]); shas.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {c}.npy")
    (od / "COLUMNS.txt").write_text("\n".join(write) + "\n"); (od / "SHA256SUMS").write_text("\n".join(shas) + "\n")
    q = {c: [float(np.nanquantile(cols[c], qq)) for qq in (0.001, 0.01, 0.5, 0.99, 0.999)] for c in R.COLUMNS}
    nz = {c: float(np.mean(cols[c][ok] != 0.0)) for c in R.COLUMNS}
    summ = dict(stratum=stratum, seed=k, rows=n, not_computed=int((~ok).sum()), E_fallback=int((fb & ok).sum()), columns_written=write, free_gib_at_write=gib,
                quantiles=q, share_nonzero=nz, scored_any_share=A.n_scored_any / max(1, A.n_ok), seconds=time.time() - t0, impacts32_sha=W.sha(sd / "impacts32.npy"),
                run_json=dict(code_revision=meta.get("code_revision"), config_paths=meta.get("config_paths")), logon=logon)
    Wsub = Wt[:, np.concatenate(sub["row"])] if sub["row"] else np.zeros((12, 0))
    np.savez_compressed(od / "subsample.npz", **{k_: np.concatenate(v) for k_, v in sub.items()}, W=Wsub.astype(np.float64), stratum=stratum, seed=k)
    A.dump(od / "acc.npz", dict(stratum=stratum, seed=k, eta_eval=M.eta_eval, imos_tl="imos_tl_ram_arc.csv (A4)" if RAMGRID else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share))
    summ["imos_tl"] = "imos_tl_ram_arc.csv (A4)" if RAMGRID else "imos_tl_ramcorr_arc.csv"; summ["ramgrid_covered_share"] = M.ramgrid_covered_share
    (Path(stg) / "_parts").mkdir(exist_ok=True); (Path(stg) / "_parts" / f"{stratum}_{k}.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(f"done {stratum}/seed-{k} in {time.time() - t0:.0f} s; wrote {write}", flush=True)


def run_supplement(stg):
    """Northern supplement rows (technique >= 1) with native lnw:comb weights at every p (gap G-W1); statistics and subsample only."""
    M = Machinery(imos_ramgrid=RAMGRID); t0 = time.time(); z = np.load(R.SUPPLEMENT); sel = z["technique"] >= 1
    t = z["t_impact_s"][sel].astype(float) + R.T0; lat = z["latitude_deg"][sel].astype(float); lon = z["longitude_deg"][sel].astype(float)
    fam = z["family4_code"][sel].astype(float); E = z["latent:impact_energy_transferred_j"][sel].astype(float)
    v2 = z["velocity_east_mps"][sel].astype(float) ** 2 + z["velocity_north_mps"][sel].astype(float) ** 2 + z["velocity_up_mps"][sel].astype(float) ** 2
    Efb = 0.5 * z["mass_kg"][sel].astype(float) * v2; fb = ~np.isfinite(E) & np.isfinite(Efb); E = np.where(fb, Efb, E)
    tau = np.full(len(t), np.nan)
    # the reduced file carries no tau90: draw tau from the run J tau90 distribution of rows within +/-1 deg (declared gap G11-3)
    n = len(t); ok = np.isfinite(t) & np.isfinite(lat) & np.isfinite(lon) & np.isfinite(E) & (E > 0)
    rng = np.random.default_rng([R.SEED, R.BLOCK, 9, 0]); Lcal = rng.normal(0.0, R.CAL_L_SD_DB, n)
    # log-normal fit through the block 7 tau90 quantiles 5/50/95 % (0.11 / 3.30 / 10.59 s) -- declared stand-in for the supplement only
    q05, q50, q95 = 0.11, 3.30, 10.59; mu = np.log(q50); sdv = (np.log(q95) - np.log(q05)) / (2 * 1.6449)
    tau = np.exp(rng.normal(mu, sdv, n))
    Wt = np.zeros((12, n))
    for i, o in enumerate(R.OPTIONS):
        w = np.exp(z[f"lnw:comb/{o}"][sel].astype(float)); w[~np.isfinite(w)] = 0.0
        for j, p in enumerate(R.PS): Wt[3 * i + j] = w * ok
    A = Acc(len(M.eta_eval)); A.n_rows = n; A.n_ok = int(ok.sum()); A.n_E_fallback = int((fb & ok).sum())
    sub = {k_: [] for k_ in ("row", "lat", "lon", "t", "E", "tau", "fam", "Lcal", "lnL_grid", "lnL_grid_ims", "lnL_marg_imos", "lnL_marg_ims")}
    for s in range(0, n, R.CHUNK_ROWS):
        e = min(n, s + R.CHUNK_ROWS); m = ok[s:e]; idx = np.arange(s, e)[m]
        lnL = {}; lnPnd = {}; lnL_ims = {}; lnPnd_ims = {}
        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau[idx]); lnL_A = {} if STATS_ONLY else None
        for a in R.ALPHAS:
            if STATS_ONLY:
                l_g, p_g, nsc, l_a = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED, amp=True); lnL_A[a] = l_a
            else:
                l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY: A.n_scored_any += int((nsc + nsc_i > 0).sum())
        ap = R.ALPHA_PRIMARY; lm = M.marg(lnL[ap]); lmi = M.marg(lnL_ims[ap])
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)), lnL_A)
        ss = idx[(idx % 2) == 0]; pos = np.searchsorted(idx, ss)   # 1 in 2 of the supplement rows
        sub["row"].append(ss); sub["lat"].append(lat[ss]); sub["lon"].append(lon[ss]); sub["t"].append(t[ss]); sub["E"].append(E[ss]); sub["tau"].append(tau[ss])
        sub["fam"].append(fam[ss]); sub["Lcal"].append(Lcal[ss]); sub["lnL_grid"].append(lnL[ap][pos].astype(np.float32)); sub["lnL_grid_ims"].append(lnL_ims[ap][pos].astype(np.float32))
        sub["lnL_marg_imos"].append(lm[pos]); sub["lnL_marg_ims"].append(lmi[pos])
        print(f"supplement: rows {e}/{n} {time.time() - t0:.0f} s", flush=True)
    od = Path(stg) / "supplement"; od.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(od / "subsample.npz", **{k_: np.concatenate(v) for k_, v in sub.items()}, W=Wt[:, np.concatenate(sub["row"])], stratum="supplement", seed=0)
    A.dump(od / "acc.npz", dict(stratum="supplement", seed=0, eta_eval=M.eta_eval, tau_standin="log-normal through tau90 q05/50/95 = 0.11/3.30/10.59 s"))
    share = {o: dict(supplement=float(np.exp(z[f"lnw:comb/{o}"][sel].astype(float))[np.isfinite(z[f"lnw:comb/{o}"][sel])].sum()),
                     total=float(np.nansum(np.exp(z[f"lnw:comb/{o}"].astype(float))))) for o in R.OPTIONS}
    (Path(stg) / "_parts").mkdir(exist_ok=True)
    (Path(stg) / "_parts" / "supplement.json").write_text(json.dumps(dict(rows=n, used=int(ok.sum()), share=share, seconds=time.time() - t0, sha=W.sha(R.SUPPLEMENT)), indent=1) + "\n")
    print(f"done supplement in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "supplement": run_supplement(sys.argv[3])
    else: run_seed(sys.argv[1], int(sys.argv[2]), sys.argv[3])
