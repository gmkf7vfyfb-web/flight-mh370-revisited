cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("common.py").read()
s=s.replace('''class Machinery:
    def __init__(self):
        # --- TL tables (arc grid, offset 0, 10 m, ridge rows kept); IMS raw KRAKEN minus imp500 RAM delta (as apply_to_model)
        xs, tabs = TT.load_table(R.RD / "tl_grid_run_j", list(R.BANDS_HZ), [R.TL_SRC_DEPTH_M])
''','''class Machinery:
    def __init__(self, imos_ramgrid=False):
        # --- TL tables (arc grid, offset 0, 10 m, ridge rows kept); IMS raw KRAKEN minus imp500 RAM delta (as apply_to_model)
        xs, tabs = TT.load_table(R.RD / "tl_grid_run_j", list(R.BANDS_HZ), [R.TL_SRC_DEPTH_M])
        self.imos_ramgrid = imos_ramgrid; self.ramgrid_covered_share = None
        if imos_ramgrid:   # amendment A4: IMOS tables from the RAM-along-grid drop-in (uncovered rows keep the old value inside the file)
            xs2, tabs2 = TT.load_table(R.TL_TABLE_DIR_RAMGRID, list(R.BANDS_HZ), [R.TL_SRC_DEPTH_M], imos_file=R.IMOS_TL_FILE_RAMGRID)
            assert np.allclose(xs2, xs), "RAM-grid table latitude nodes differ from the arc grid"
            for rx in R.RECEIVERS_GATED: tabs[rx] = tabs2[rx]
            g = pd.read_csv(R.TL_TABLE_DIR_RAMGRID / R.IMOS_TL_FILE_RAMGRID, dtype={"logger": str})
            g = g[(g.offset_nm == 0) & np.isclose(g.src_depth_m, R.TL_SRC_DEPTH_M) & g.logger.isin(R.RECEIVERS_GATED) & g.tl_db.notna()]
            self.ramgrid_covered_share = {rx: float(g[g.logger == rx].ram_grid_covered.mean()) for rx in R.RECEIVERS_GATED}
''')
s=s.replace('''                self.cands[(rx, a)] = c[["t_unix", "p", "time_utc", "eta_needed"]].reset_index(drop=True)
            c = pc[(pc.receiver == "H01W")''','''                self.cands[(rx, a)] = c[["t_unix", "p", "time_utc", "eta_needed", "excess_5_40_pa2s"]].reset_index(drop=True)
            c = pc[(pc.receiver == "H01W")''')
# amplitude-weighted match
s=s.replace('''    # ---------------------------------------------------------------- per-row likelihood on the eta grid''','''    def match_amp(self, rx, alpha, t_pred, d_km, log_se):
        """Amendment A4(c): m_r^A / beta_r [n, K] = timing kernel x amplitude-consistency weight exp(-0.5 ((log10 E_c - log10 SE)/sigma)^2);
        log_se [n, K] = log10 of the predicted received 5-40 Hz band energy (Pa^2 s) per row and eta. Down-weighting only."""
        c = self.cands[(rx, alpha)]; beta = alpha / R.WINDOW_S
        sig = np.sqrt((d_km * R.C_SOFAR_SD / R.C_SOFAR ** 2) ** 2 + R.SIGMA_INJ_S ** 2 + R.SIGMA_CLOCK_S ** 2)
        m = np.zeros(log_se.shape)
        for tc, ec in zip(c.t_unix.values, c.excess_5_40_pa2s.values):
            z = (t_pred - tc) / sig
            kt = np.where(np.abs(z) <= R.KERNEL_TRUNC_SIGMA, np.exp(-0.5 * z * z) / (np.sqrt(2 * np.pi) * sig), 0.0)
            if not np.isfinite(ec) or ec <= 0: continue
            ka = np.exp(-0.5 * ((np.log10(ec) - log_se) / R.SIGMA_A_DECADES) ** 2)
            m += kt[:, None] * ka
        return m / beta

    # ---------------------------------------------------------------- per-row likelihood on the eta grid''')
s=s.replace('''    def lnL_grid(self, P_, Lcal, alpha, receivers):
        """Returns lnL[n, K] = sum_r ln L_r and lnPnd[n, K] = sum_r ln(1 - P_D,r) over the receivers whose predicted arrival
        lies in a scored window (others contribute 0 = no information), and the count of scored receivers per row."""
        n = P_["n"]; K = len(self.eta_eval)
        lnL = np.zeros((n, K)); lnPnd = np.zeros((n, K)); nsc = np.zeros(n, np.int8)
        for rx in receivers:
            sc = P_["sc"][rx]
            if not sc.any(): continue
            nsc[sc] += 1
            snr = P_["base"][rx][sc][:, None] + 10 * self.log10eta[None, :] + Lcal[sc][:, None]
            P = self.pd(rx, alpha, snr, P_["ti"][sc]); mr = self.match(rx, alpha, P_["tp"][rx][sc], P_["d"][rx][sc])
            Lr = (1 - P) + P * mr[:, None]
            lnL[sc] += np.log(np.maximum(Lr, 1e-300)); lnPnd[sc] += np.log(np.maximum(1 - P, 1e-300))
        return lnL, lnPnd, nsc''','''    def lnL_grid(self, P_, Lcal, alpha, receivers, amp=False):
        """Returns lnL[n, K] = sum_r ln L_r and lnPnd[n, K] = sum_r ln(1 - P_D,r) over the receivers whose predicted arrival
        lies in a scored window (others contribute 0 = no information), and the count of scored receivers per row.
        amp=True (amendment A4c) also returns lnL_A with the amplitude-consistency-weighted match (IMOS receivers only)."""
        n = P_["n"]; K = len(self.eta_eval)
        lnL = np.zeros((n, K)); lnPnd = np.zeros((n, K)); nsc = np.zeros(n, np.int8); lnLA = np.zeros((n, K)) if amp else None
        for rx in receivers:
            sc = P_["sc"][rx]
            if not sc.any(): continue
            nsc[sc] += 1
            snr = P_["base"][rx][sc][:, None] + 10 * self.log10eta[None, :] + Lcal[sc][:, None]
            P = self.pd(rx, alpha, snr, P_["ti"][sc]); mr = self.match(rx, alpha, P_["tp"][rx][sc], P_["d"][rx][sc])
            Lr = (1 - P) + P * mr[:, None]
            lnL[sc] += np.log(np.maximum(Lr, 1e-300)); lnPnd[sc] += np.log(np.maximum(1 - P, 1e-300))
            if amp and rx in R.RECEIVERS_GATED:
                log_se = (snr + self.bmed[rx]) / 10.0 - 12.0 + np.log10(self.teff[rx][P_["ti"][sc]])[:, None]
                mA = self.match_amp(rx, alpha, P_["tp"][rx][sc], P_["d"][rx][sc], log_se)
                lnLA[sc] += np.log(np.maximum((1 - P) + P * mA, 1e-300))
            elif amp:
                lnLA[sc] += np.log(np.maximum(Lr, 1e-300))
        return (lnL, lnPnd, nsc, lnLA) if amp else (lnL, lnPnd, nsc)''')
open("common.py","w").write(s); print("common ok")

w=open("worker.py").read()
# Acc: amplitude variant sums
w=w.replace('''        self.wLfixed = z(12, 3); self.wLfixed_ims = z(12, 3)''','''        self.wLfixed = z(12, 3); self.wLfixed_ims = z(12, 3)
        self.wL_A = {a: z(12, NB1, K) for a in R.ALPHAS}; self.half_wLA = {a: z(12, NBH) for a in R.ALPHAS}; self.wLmarg_A = {a: z(12) for a in R.ALPHAS}; self.fam_wLA = z(12, 4)''')
w=w.replace('''    def add(self, Wt, lat, lon, fam, lnL, lnPnd, lnL_ims, lnPnd_ims, M, mask):''','''    def add(self, Wt, lat, lon, fam, lnL, lnPnd, lnL_ims, lnPnd_ims, M, mask, lnL_A=None):''')
w=w.replace('''            lm = M.marg(lnL[a]); lmi = M.marg(lnL_ims[a]); eLm = np.exp(np.clip(lm, -700, 700)); eLmi = np.exp(np.clip(lmi, -700, 700))
            for j in range(12):
                w = Wt[j] * mask''','''            lm = M.marg(lnL[a]); lmi = M.marg(lnL_ims[a]); eLm = np.exp(np.clip(lm, -700, 700)); eLmi = np.exp(np.clip(lmi, -700, 700))
            if lnL_A is not None:
                LA = np.exp(np.clip(lnL_A[a], -700, 700)); eLmA = np.exp(np.clip(M.marg(lnL_A[a]), -700, 700))
            for j in range(12):
                w = Wt[j] * mask
                if lnL_A is not None:
                    self.wLmarg_A[a][j] += np.sum(w * eLmA); self.half_wLA[a][j] += np.bincount(bh, weights=w * eLmA, minlength=NBH)
                    if a == R.ALPHA_PRIMARY:
                        for k in range(4):
                            m = fi == k; self.fam_wLA[j, k] += np.sum(w[m] * eLmA[m])''')
w=w.replace('''                self.wPnd[a][j] += Wb @ P; self.wL[a][j] += Wb @ L; self.wPnd_ims[a][j] += Wb @ Pi; self.wL_ims[a][j] += Wb @ Li''','''                self.wPnd[a][j] += Wb @ P; self.wL[a][j] += Wb @ L; self.wPnd_ims[a][j] += Wb @ Pi; self.wL_ims[a][j] += Wb @ Li
                if lnL_A is not None: self.wL_A[a][j] += Wb @ LA''')
w=w.replace('''            d[f"half_wL_{t}"] = self.half_wL[a]; d[f"half_wLims_{t}"] = self.half_wLims[a]; d[f"wLmarg_{t}"] = self.wLmarg[a]; d[f"wLmarg_ims_{t}"] = self.wLmarg_ims[a]''','''            d[f"half_wL_{t}"] = self.half_wL[a]; d[f"half_wLims_{t}"] = self.half_wLims[a]; d[f"wLmarg_{t}"] = self.wLmarg[a]; d[f"wLmarg_ims_{t}"] = self.wLmarg_ims[a]
            d[f"wL_A_{t}"] = self.wL_A[a]; d[f"half_wLA_{t}"] = self.half_wLA[a]; d[f"wLmarg_A_{t}"] = self.wLmarg_A[a]
        d["fam_wLA"] = self.fam_wLA''')
# stats-only mode: env B11_STATS_ONLY=1 -> Machinery(imos_ramgrid=True), amp variant, no columns, output dir = stg (caller passes stats dir)
w=w.replace('''def run_seed(stratum, k, stg):
    M = Machinery(); t0 = time.time()''','''STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: RAM-grid IMOS TL, amplitude variant, statistics only


def run_seed(stratum, k, stg):
    M = Machinery(imos_ramgrid=STATS_ONLY); t0 = time.time()''')
w=w.replace('''        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau90[idx])
        for a in R.ALPHAS:
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
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)))''','''        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau90[idx]); lnL_A = {} if STATS_ONLY else None
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
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)), lnL_A)''')
w=w.replace('''    od = Path(stg) / stratum / f"seed-{k}"; od.mkdir(parents=True, exist_ok=True)
    gib = free_gib(stg); write = list(R.COLUMNS) if (gib >= R.DISK_FLOOR_GIB or os.environ.get("B11_TOPUP") == "1") else ["hydro-lnL-imos-margeta"]''','''    od = Path(stg) / stratum / f"seed-{k}"; od.mkdir(parents=True, exist_ok=True)
    gib = free_gib(stg); write = list(R.COLUMNS) if (gib >= R.DISK_FLOOR_GIB or os.environ.get("B11_TOPUP") == "1") else ["hydro-lnL-imos-margeta"]
    if STATS_ONLY: write = []      # amendment A4(b): no columns''')
w=w.replace('''    A.dump(od / "acc.npz", dict(stratum=stratum, seed=k, eta_eval=M.eta_eval))
    (Path(stg) / "_parts").mkdir(exist_ok=True); (Path(stg) / "_parts" / f"{stratum}_{k}.json").write_text(json.dumps(summ, indent=1) + "\\n")''','''    A.dump(od / "acc.npz", dict(stratum=stratum, seed=k, eta_eval=M.eta_eval, imos_tl="imos_tl_ram_arc.csv (A4)" if STATS_ONLY else "imos_tl_ramcorr_arc.csv", ramgrid_covered_share=M.ramgrid_covered_share))
    summ["imos_tl"] = "imos_tl_ram_arc.csv (A4)" if STATS_ONLY else "imos_tl_ramcorr_arc.csv"; summ["ramgrid_covered_share"] = M.ramgrid_covered_share
    (Path(stg) / "_parts").mkdir(exist_ok=True); (Path(stg) / "_parts" / f"{stratum}_{k}.json").write_text(json.dumps(summ, indent=1) + "\\n")''')
# supplement: same
w=w.replace('''def run_supplement(stg):
    """Northern supplement rows (technique >= 1) with native lnw:comb weights at every p (gap G-W1); statistics and subsample only."""
    M = Machinery(); t0 = time.time()''','''def run_supplement(stg):
    """Northern supplement rows (technique >= 1) with native lnw:comb weights at every p (gap G-W1); statistics and subsample only."""
    M = Machinery(imos_ramgrid=STATS_ONLY); t0 = time.time()''')
w=w.replace('''        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau[idx])
        for a in R.ALPHAS:
            l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY: A.n_scored_any += int((nsc + nsc_i > 0).sum())
        ap = R.ALPHA_PRIMARY; lm = M.marg(lnL[ap]); lmi = M.marg(lnL_ims[ap])
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)))''','''        PP = M.prep(t[idx], lat[idx], lon[idx], E[idx], tau[idx]); lnL_A = {} if STATS_ONLY else None
        for a in R.ALPHAS:
            if STATS_ONLY:
                l_g, p_g, nsc, l_a = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED, amp=True); lnL_A[a] = l_a
            else:
                l_g, p_g, nsc = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_GATED)
            l_i, p_i, nsc_i = M.lnL_grid(PP, Lcal[idx], a, R.RECEIVERS_PROXY)
            lnL[a] = l_g; lnPnd[a] = p_g; lnL_ims[a] = l_g + l_i; lnPnd_ims[a] = p_g + p_i
            if a == R.ALPHA_PRIMARY: A.n_scored_any += int((nsc + nsc_i > 0).sum())
        ap = R.ALPHA_PRIMARY; lm = M.marg(lnL[ap]); lmi = M.marg(lnL_ims[ap])
        A.add(Wt[:, idx], lat[idx], lon[idx], fam[idx], lnL, lnPnd, lnL_ims, lnPnd_ims, M, np.ones(len(idx)), lnL_A)''')
open("worker.py","w").write(w); print("worker ok")
d=open("driver.py").read()
d=d.replace('''NPROC = int(sys.argv[1]) if len(sys.argv) > 1 else R.N_PROC
out = R.EXCHANGE_OUT; stg = pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)''','''NPROC = int(sys.argv[1]) if len(sys.argv) > 1 else R.N_PROC
STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: statistics-only re-run into stats-ramgrid/, no columns, no finaliser
out = R.STATS_DIR_RAMGRID if STATS_ONLY else R.EXCHANGE_OUT; stg = out if STATS_ONLY else pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)''')
d=d.replace('''say(f"all tasks ended in {time.time() - t0:.0f}s failed={failed}")
if failed: sys.exit(1)''','''say(f"all tasks ended in {time.time() - t0:.0f}s failed={failed}")
if failed: sys.exit(1)
if STATS_ONLY:
    (stg / "DONE").write_text(f"statistics-only re-run (amendment A4, RAM-grid IMOS TL) finished {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\\n"); say("DONE (stats only)"); sys.exit(0)''')
open("driver.py","w").write(d); print("driver ok")
EOF
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 B11_STATS_ONLY=1 python - <<'EOF' 2>&1 | grep -v Warn
import numpy as np, sys, time; sys.path.insert(0,'.'); sys.path.insert(0,'..')
import prereg as R, run_j_windows as W
from common import Machinery
M=Machinery(imos_ramgrid=True); M0=Machinery(); print("covered", M.ramgrid_covered_share)
sd=R.RUN_J/"run-j-waypoints"/"seed-1"; g,meta,n=W.load_seed(sd); idx=np.arange(0,n,n//20000)[:20000]; z=np.load(sd/"tau90_v1.npz")
t=g("unix_s")[idx]; lat=g("latitude_deg")[idx]; lon=g("longitude_deg")[idx]; E=z["energy_transferred_j"][idx].astype(float); tau=z["tau90_s"][idx].astype(float)
PP=M.prep(t,lat,lon,E,tau); PP0=M0.prep(t,lat,lon,E,tau)
print("base median new vs old:", {rx:(round(float(np.nanmedian(PP["base"][rx])),1), round(float(np.nanmedian(PP0["base"][rx])),1)) for rx in R.RECEIVERS_GATED})
Lcal=np.random.default_rng(1).normal(0,10,len(idx)); t1=time.time()
lnL,lnP,nsc,lnLA=M.lnL_grid(PP,Lcal,0.05,R.RECEIVERS_GATED,amp=True); print("time", round(time.time()-t1,2))
print("marg full q", np.round(np.quantile(M.marg(lnL),[0,.01,.5,.99,1]),3)); print("marg amp q", np.round(np.quantile(M.marg(lnLA),[0,.01,.5,.99,1]),3)); print("Pnd(1e-2) new", round(float(np.exp(lnP[:,40]).mean()),3))
k=lnL[:,40]!=lnLA[:,40]; print("rows where amp differs at 1e-2", int(k.sum()), "max lnL at 1e-2 full/amp", round(float(lnL[:,40].max()),2), round(float(lnLA[:,40].max()),3))
EOF