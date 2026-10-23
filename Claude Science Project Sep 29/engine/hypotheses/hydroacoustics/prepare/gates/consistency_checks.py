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
   Round-3 verifier fix (23 Oct 05:15 UTC): (a) H08S is NOT ASSESSABLE for silence: the airgun survey dominates the record and its
   P_D comes from a proxy noise without the survey; (b) "not silent" uses every register single at that receiver with p <= 0.05
   (all detectors, raw and residual panels), plus the M1b candidate lists, within 3 sigma; sigma for this window includes the
   module pick convention (pick_sd 10 s, registry CONVENTION_NO_LOCATED_SOURCE) so that the window is wide (fewer silence labels).
   Common-source timing: exclusion uses the pre-registered likelihood timing kernel (no pick term); zmax_pick10 (with 10 s pick sd
   per member) is a sensitivity output only.
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

    PICK_SD = 10.0

    def sigma(self, d, pick=0.0):
        return np.sqrt((d * CSD / C ** 2) ** 2 + R.SIGMA_INJ_S ** 2 + R.SIGMA_CLOCK_S ** 2 + pick ** 2)

    def set_register_singles(self, singles):
        """singles: register v2 singles DataFrame (rx, time_utc, p). Used for the 'not silent' check (all detectors)."""
        self.reg = {}
        for rx, g in singles[singles.p <= 0.05].groupby(singles.rx.astype(str)):
            self.reg[rx] = np.array([hms(t) for t in g.time_utc])

    def common_source(self, members, lat, lon, t_imp):
        d = self.M.distances_km(np.array([lat]), np.array([lon])); out = []
        for rx, t in members:
            if rx not in d: continue
            dd = float(d[rx][0]); r_ = hms(t) - dd / C - t_imp
            out.append((rx, t, float(r_ / self.sigma(dd)), float(r_ / self.sigma(dd, self.PICK_SD))))
        zmax = max(abs(z) for _, _, z, _ in out) if out else np.nan
        zmax10 = max(abs(z) for _, _, _, z in out) if out else np.nan
        return zmax, zmax10, "; ".join(f"{rx} {t}: z {z:+.1f}" for rx, t, z, _ in out)

    def silence(self, member_rx, lat, lon, t_imp, E, eta):
        if not (np.isfinite(lat) and np.isfinite(t_imp) and np.isfinite(E) and np.isfinite(eta) and eta > 0):
            return np.nan, np.nan, ""
        tau = self.tau_med(lat)
        P = self.M.prep(np.array([t_imp]), np.array([lat]), np.array([lon]), np.array([E]), np.array([tau]))
        ps, ps2, txt, n_ass = 1.0, 1.0, [], 0
        for rx in R.RECEIVERS:
            if rx in member_rx or not P["sc"][rx][0]: continue
            if rx == "H08S":
                txt.append("H08S: not assessable (airgun survey dominates)"); continue
            tp = P["tp"][rx][0]; sg = self.sigma(P["d"][rx][0], self.PICK_SD)
            cand = self.M.cands[(rx, 0.05)]
            ct = np.concatenate([cand.t_unix.values if len(cand) else np.array([]), getattr(self, "reg", {}).get(rx, np.array([]))])
            if len(ct) and np.any(np.abs(ct - tp) <= 3 * sg):
                txt.append(f"{rx}: detection within 3 sigma (not silent)"); continue
            snr = P["base"][rx][0] + 10 * np.log10(eta)
            pd1 = float(self.M.pd(rx, 0.05, np.array([[snr]]), P["ti"])[0, 0]); pd2 = float(self.M.pd(rx, 0.05, np.array([[snr - 9.5]]), P["ti"])[0, 0])
            n_ass += 1; ps *= 1 - pd1; ps2 *= 1 - pd2; txt.append(f"{rx}: SNR {snr:+.1f} dB, P_D {pd1:.2f} (D05 -9.5 dB: {pd2:.2f})")
        if n_ass == 0:   # no non-member receiver could be assessed for silence: not assessed (not "consistent")
            return np.nan, np.nan, "; ".join(txt + ["silence not assessed (no assessable non-member receiver)"])
        return ps, ps2, "; ".join(txt)
