"""Block 11 shared machinery (prereg.py sections 2-7): TL tables, received-level base, P_D fits, scored windows, matched
candidates, per-row likelihood on the eta grid. Imported by worker.py (per seed / supplement) and reduce.py (conditionals).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R
import tl_grid_table as TT
from imos_stageB_map import band_fraction
import run_j_windows as W

INJ = R.RD / "injection_run_j"
SRCH = R.RD / "searches_run_j"
TAU_GRID = np.logspace(np.log10(R.TAU_CLIP[0]), np.log10(R.TAU_CLIP[1]), 80)


def hms_to_unix(s):
    h, m, sec = s.split(":")
    return R.T0 + 3600 * int(h) + 60 * int(m) + float(sec)


class Machinery:
    def __init__(self):
        # --- TL tables (arc grid, offset 0, 10 m, ridge rows kept); IMS raw KRAKEN minus imp500 RAM delta (as apply_to_model)
        xs, tabs = TT.load_table(R.RD / "tl_grid_run_j", list(R.BANDS_HZ), [R.TL_SRC_DEPTH_M])
        rd = pd.read_csv(R.RD / "near_limits/ims_ram_delta.csv")
        self.xs = xs; self.tl = {}
        for rx in R.RECEIVERS:
            T = np.vstack([tabs[rx][(fc, R.TL_SRC_DEPTH_M)] for fc in R.BANDS_HZ]).T.astype(float)   # [lat, band]
            if rx in R.RECEIVERS_PROXY:
                dd = rd[rd.path == f"imp500_{rx}"]; h = dd[np.isclose(dd.src_depth_m, 10.0)].set_index("fc_hz").delta_db
                delta = np.array([np.interp(np.log10(fc), np.log10(h.index.values), h.values) for fc in R.BANDS_HZ])
                T = T - delta[None, :]
            self.tl[rx] = T
        # --- band fractions on the tau grid (ESD flat to 1/tau, f^-2 above)
        self.Sb = np.vstack([band_fraction(fc, 1.0 / TAU_GRID, 2.0) for fc in R.BANDS_HZ]).T     # [tau, band]
        # --- block 7 summary: background medians, T_eff per tau cell, fits
        self.summ = json.load(open(INJ / "summary.json")); self.fits = json.load(open(INJ / "fits.json"))
        self.taus = np.array([float(v) for v in self.summ["taus"]])
        self.bmed = {rx: self.summ["bg_median_level_db"][rx] + self.summ["abs_offset_db"][rx] for rx in R.RECEIVERS}
        self.teff = {}
        for rx in R.RECEIVERS:
            te = self.summ["t_eff_s"][rx]
            self.teff[rx] = np.array([np.mean([v for k, v in te.items() if abs(float(k.split("|")[1]) - t) < 1e-9]) for t in self.taus])
        self.pd_par = {}   # (rx, alpha) -> (L50[3], slope[3], valid[3])
        self.pd_missing = []
        for rx in R.RECEIVERS:
            for a in R.ALPHAS:
                l50 = np.full(3, np.nan); sl = np.full(3, np.nan)
                for i, t in enumerate(self.taus):
                    f = self.fits.get(f"{rx}|{R.METHOD}|{a}|{t}", {})
                    if f.get("L50_re_noise_db") is not None and f.get("slope_db") is not None:
                        l50[i], sl[i] = f["L50_re_noise_db"], f["slope_db"]
                    else:
                        self.pd_missing.append(f"{rx}|{a}|{t:.3g}")
                self.pd_par[(rx, a)] = (l50, sl, np.isfinite(l50) & np.isfinite(sl))
        # --- receivers, scored windows, candidates
        rxpos = W.receivers(); self.rxpos = {rx: rxpos[rx] for rx in R.RECEIVERS}
        iw = pd.read_csv(SRCH / "imos/imos_windows.csv", dtype={"receiver": str}); pw = pd.read_csv(SRCH / "panels/panel_windows.csv")
        self.windows = {}
        for rx in R.RECEIVERS_GATED:
            st = np.array(sorted({hms_to_unix(s) for s in iw[iw.receiver == rx].window_start_utc}))
            self.windows[rx] = st
        for rx in R.RECEIVERS_PROXY:
            st = np.array(sorted({hms_to_unix(s) for s in pw[pw.receiver == rx].window_start_utc}))
            self.windows[rx] = st
        ic = pd.read_csv(SRCH / "imos/imos_candidates.csv", dtype={"receiver": str}); pc = pd.read_csv(SRCH / "panels/panel_candidates.csv")
        self.cands = {}
        for a in R.ALPHAS:
            for rx in R.RECEIVERS_GATED:
                c = ic[(ic.receiver == rx) & (ic.detector == "M1b") & (ic.p <= a)]
                self.cands[(rx, a)] = c[["t_unix", "p", "time_utc", "eta_needed"]].reset_index(drop=True)
            c = pc[(pc.receiver == "H01W") & (pc.detector == "M1b") & (pc.p <= a)]
            self.cands[("H01W", a)] = c[["t_unix", "p", "time_utc", "eta_needed"]].reset_index(drop=True)
            c = pc[(pc.receiver == "H08S") & (pc.detector == "M1b_res") & (pc.p_B <= a)]       # residual rows only (G-S9)
            self.cands[("H08S", a)] = c[["t_unix", "p", "time_utc", "eta_needed"]].reset_index(drop=True)
        # evaluation set: the 41-point prior grid (marginal) followed by the three fixed eta values (exact)
        self.eta_eval = np.concatenate([R.ETA_GRID, np.array(list(R.ETA_FIXED.values()))])
        self.n_grid = len(R.ETA_GRID)
        self.log10eta = np.log10(self.eta_eval)

    # ---------------------------------------------------------------- geometry
    def distances_km(self, lat, lon):
        from pyproj import Geod
        g = Geod(ellps="WGS84"); out = {}
        for rx, (rlat, rlon) in self.rxpos.items():
            _, _, d = g.inv(lon, lat, np.full_like(lon, rlon), np.full_like(lat, rlat)); out[rx] = d / 1000.0
        return out

    def in_scored(self, rx, t):
        st = self.windows[rx]
        if len(st) == 0: return np.zeros(len(t), bool)
        i = np.searchsorted(st, t, side="right") - 1
        ok = i >= 0; j = np.clip(i, 0, len(st) - 1)
        return ok & (t - st[j] <= R.WINDOW_S) & (t >= st[j])

    def tau_cell(self, tau):
        return np.abs(np.log(tau)[:, None] - np.log(self.taus)[None, :]).argmin(1)

    # ---------------------------------------------------------------- level
    def level_base(self, lat, E, tau):
        """base_r = 10 log10(F_r / 1e-12) + G_r - B_r  so that S_r(eta) = base_r + 10 log10(eta) + L_cal. Blocked (all bands
        NaN) -> -inf. Returns dict rx -> base[n], and the tau-cell index."""
        tau_c = np.clip(tau, R.TAU_CLIP[0], R.TAU_CLIP[1]); lt = np.log10(tau_c)
        Sb = np.vstack([np.interp(lt, np.log10(TAU_GRID), self.Sb[:, j]) for j in range(len(R.BANDS_HZ))]).T   # [n, band]
        ti = self.tau_cell(tau_c); la = np.clip(lat, self.xs.min(), self.xs.max()); base = {}
        for rx in R.RECEIVERS:
            T = self.tl[rx]; acc = np.zeros(len(lat))
            for j in range(len(R.BANDS_HZ)):
                tlb = TT.tl_at(self.xs, T[:, j], la)
                acc += Sb[:, j] * np.nan_to_num(10 ** (-tlb / 10), nan=0.0)
            F = E * R.RHO_C / (2 * np.pi) * acc / self.teff[rx][ti]
            with np.errstate(divide="ignore"):
                b = 10 * np.log10(F / 1e-12)
            if rx in R.RECEIVERS_PROXY: b = b + R.TRIAD_GAIN_DB
            base[rx] = b - self.bmed[rx]
        return base, ti

    def pd(self, rx, alpha, snr, ti):
        """snr: [n, k] array (dB re background median); ti: tau cell per row. Missing fit -> 0."""
        l50, sl, ok = self.pd_par[(rx, alpha)]
        L = l50[ti][:, None]; S = sl[ti][:, None]
        with np.errstate(over="ignore", invalid="ignore"):
            p = 1.0 / (1.0 + np.exp(-(snr - L) / S))
        p = np.where(ok[ti][:, None], p, 0.0)
        return np.nan_to_num(p, nan=0.0)

    def match(self, rx, alpha, t_pred, d_km):
        """m_r / beta_r per row (dimensionless): Gaussian timing kernel over the receiver's candidates at p <= alpha."""
        c = self.cands[(rx, alpha)]; beta = alpha / R.WINDOW_S
        sig = np.sqrt((d_km * R.C_SOFAR_SD / R.C_SOFAR ** 2) ** 2 + R.SIGMA_INJ_S ** 2 + R.SIGMA_CLOCK_S ** 2)
        m = np.zeros(len(t_pred))
        for tc in c.t_unix.values:
            z = (t_pred - tc) / sig
            m += np.where(np.abs(z) <= R.KERNEL_TRUNC_SIGMA, np.exp(-0.5 * z * z) / (np.sqrt(2 * np.pi) * sig), 0.0)
        return m / beta

    # ---------------------------------------------------------------- per-row likelihood on the eta grid
    def prep(self, t, lat, lon, E, tau):
        """Geometry and level base shared by every alpha and receiver set."""
        d = self.distances_km(lat, lon); base, ti = self.level_base(lat, E, tau)
        tp = {rx: t + d[rx] / R.C_SOFAR for rx in R.RECEIVERS}
        sc = {rx: self.in_scored(rx, tp[rx]) & np.isfinite(base[rx]) for rx in R.RECEIVERS}
        return dict(d=d, base=base, ti=ti, tp=tp, sc=sc, n=len(t))

    def lnL_grid(self, P_, Lcal, alpha, receivers):
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
        return lnL, lnPnd, nsc

    def marg(self, lnL):
        """ln sum_k omega_k exp(lnL_k) over the 41 prior grid points with equal omega (log-uniform prior)."""
        g = lnL[:, :self.n_grid]; m = g.max(1, keepdims=True)
        return (m + np.log(np.mean(np.exp(g - m), axis=1, keepdims=True)))[:, 0]

    def fixed(self, lnL, name):
        """Column of the exact fixed eta value `name` (prereg ETA_FIXED key)."""
        return lnL[:, self.n_grid + list(R.ETA_FIXED).index(name)]
