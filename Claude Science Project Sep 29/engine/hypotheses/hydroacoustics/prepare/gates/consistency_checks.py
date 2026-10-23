"""Two consistency tests for potential-signal rows (overnight 23 Oct 2026; independent verifier findings V5 and V8).

1. COMMON-SOURCE TIMING (sets of 2-3 members). For each member: implied impact time t_c - d(locus, rx)/c, c = 1.482 km/s;
   z = (member implied time - locus implied time) / sigma, sigma = sqrt((d * 0.006 / c^2)^2 + 3^2 + 2^2) s (block 11 timing kernel:
   sound-speed, injection pick and clock terms). max|z| > 3 -> "members not common-source consistent" (a physical test: one source
   cannot give these times).
2. SILENCE AT NON-MEMBER RECEIVERS (all rows). At the row's position and implied impact time, with E = q99 run J energy and the coupling
   the row needs (eta_at_q99E), tau = D0-weighted median tau90 of run J impacts within +/-1 deg: for every receiver that is not a member,
   whose predicted arrival lies in a scored window (data held), and that has no candidate at p <= 0.05 within 3 sigma of the predicted
   arrival: predicted SNR (dB re background median) and P_D (block 7 fit, alpha 0.05). P_silent = prod (1 - P_D). Sensitivity
   P_silent_D05: SNR lowered by 9.5 dB (the largest real-arrival matched-filter loss measured on the F-35A, defect D05; X06 found M1b
   detects fewer real arrivals than injection predicts). Label "silence at <rx> not consistent with the needed coupling" when
   P_silent < 0.05; this is a LABEL (P_D is optimistic, D05; IMS noise is a stand-in, D06), not an exclusion.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; MOD = HERE.parent.parent
sys.path.insert(0, str(MOD / "prepare" / "composition_run_j")); sys.path.insert(0, str(MOD / "prepare"))
import prereg as R
from common import Machinery

C, CSD = 1.482, 0.006
T0 = 1394236800.0


def hms(s):
    try:
        h, m, x = str(s).split(":"); return T0 + int(h) * 3600 + int(m) * 60 + float(x)
    except Exception:
        return np.nan


class Checks:
    def __init__(self):
        self.M = Machinery(imos_ramgrid=True)
        g = np.load("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/sample.npz")
        k = g["w_D0"] > 0; self.glat, self.gtau, self.gw = g["lat"][k], g["tau90_s"][k], g["w_D0"][k]

    def tau_med(self, lat):
        m = np.abs(self.glat - lat) <= 1.0
        if m.sum() < 20: return 3.3
        t, w = self.gtau[m], self.gw[m]; o = np.argsort(t); c = np.cumsum(w[o]) / w.sum()
        return float(t[o][min(np.searchsorted(c, 0.5), len(t) - 1)])

    def sigma(self, d):
        return np.sqrt((d * CSD / C ** 2) ** 2 + R.SIGMA_INJ_S ** 2 + R.SIGMA_CLOCK_S ** 2)

    def common_source(self, members, lat, lon, t_imp):
        d = self.M.distances_km(np.array([lat]), np.array([lon])); out = []
        for rx, t in members:
            if rx not in d: continue
            dd = float(d[rx][0]); z = (hms(t) - dd / C - t_imp) / self.sigma(dd); out.append((rx, t, float(z)))
        zmax = max(abs(z) for _, _, z in out) if out else np.nan
        return zmax, "; ".join(f"{rx} {t}: z {z:+.1f}" for rx, t, z in out)

    def silence(self, member_rx, lat, lon, t_imp, E, eta):
        if not (np.isfinite(lat) and np.isfinite(t_imp) and np.isfinite(E) and np.isfinite(eta) and eta > 0):
            return np.nan, np.nan, ""
        tau = self.tau_med(lat)
        P = self.M.prep(np.array([t_imp]), np.array([lat]), np.array([lon]), np.array([E]), np.array([tau]))
        ps, ps2, txt = 1.0, 1.0, []
        for rx in R.RECEIVERS:
            if rx in member_rx or not P["sc"][rx][0]: continue
            tp = P["tp"][rx][0]; sg = self.sigma(P["d"][rx][0])
            cand = self.M.cands[(rx, 0.05)]
            if len(cand) and np.any(np.abs(cand.t_unix.values - tp) <= 3 * sg):
                txt.append(f"{rx}: candidate within 3 sigma (not silent)"); continue
            snr = P["base"][rx][0] + 10 * np.log10(eta)
            pd1 = float(self.M.pd(rx, 0.05, np.array([[snr]]), P["ti"])[0, 0]); pd2 = float(self.M.pd(rx, 0.05, np.array([[snr - 9.5]]), P["ti"])[0, 0])
            ps *= 1 - pd1; ps2 *= 1 - pd2; txt.append(f"{rx}: SNR {snr:+.1f} dB, P_D {pd1:.2f} (D05 -9.5 dB: {pd2:.2f})")
        return ps, ps2, "; ".join(txt)
