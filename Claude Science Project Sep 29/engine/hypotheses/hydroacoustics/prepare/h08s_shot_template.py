"""PRE-REGISTRATION and implementation (Pete, 10 Oct): shape test of the H08S airgun-like shots by local
stacked templates. A coincident separate signal may modify the shoulders as well as the peak. Committed
before it was run.

DATA: Kadri (2024) Figure 9 H08S polylines (h08s_shot_outliers.load, 40 Hz).
  - The polylines are vertex-simplified, so waveform phase is not reliable. The analysis therefore works
    on the ENERGY ENVELOPE: p^2 smoothed by a 0.25 s boxcar, as log10.
  - With raw IMS data the same procedure applies to full waveforms and all three triad elements.
SHOTS: the pulses of h08s_pulse_energy.pulses with z_E_peak > -3. This excludes weak secondary pulses and
  uses no cadence or timing rule.
ALIGNMENT AND TEMPLATES:
  - Each shot's log-envelope over [-3, +6] s about its peak is aligned to the panel's median shot
    log-envelope by cross-correlation (lag within +-0.5 s).
  - LOCAL TEMPLATE for shot i: the median of the aligned log-envelopes of shots i-6 .. i+6, excluding i
    itself, each normalised to zero mean over the window first.
STATISTICS per shot:
  - rho: Pearson correlation of the shot's aligned log-envelope with its local template (shape).
  - Residual ratio in dB, per window: the shot's mean log-envelope minus the template's (both
    unnormalised; the template's offset is the shot's own level over the peak window). Windows: pre
    [-3, -1], peak [-1, 1], post [1, 4], tail [4, 6] s. A positive value means extra energy relative to
    the peak-scaled shot shape.
  - SPE: the squared prediction error of the shot's normalised log-envelope outside the first 3 principal
    components of all shots in its panel.
DEFECT DISCLOSED (10 Oct, found AFTER the first run): the 'peak' residual is identically zero by
  construction, because the template level is set from the shot's own peak-window mean. Its robust z is
  floating-point noise, and the first run flagged 17 high and 17 low 'outliers' on it. Those also
  inflated the injection P_D to a floor of about 0.25. The peak window is therefore EXCLUDED from the
  outlier and injection logic (it is still written out). Peak energy is tested in h08s_pulse_energy.py.
  The first run is kept as results-data/h08s_template/v1_defective/.
OUTLIERS (robust z = (x - median) / (1.4826 MAD) per panel):
  - SHAPE: z_rho <= -3.
  - RESIDUAL HIGH: z >= +3 in any window (primary). RESIDUAL LOW: z <= -3 (secondary).
  - SPE: z_SPE >= 3.
  - Outlier time = the shot's peak time.
COINCIDENCE, NULL, BF SWEEP: exactly as h08s_pulse_energy.py. The primary rule is span plus log10 BF >= 1
  against the stand-in PDF, with H01W strict, loose and Table 1-gated. The null is cyclic shifts of
  outlier flags over the shot list.
SENSITIVITY:
  - T_C2 injected at uniform random times, 300 per SNR in {-20, -15, -10, -6, -3, 0, 3} dB.
  - SNR = the template's peak-2 s energy over the panel's median shot E_peak.
  - Detected if the shot whose window [-3, +6] s contains the injection maximum is an outlier on any
    statistic.
OUTPUTS: h08s_template_shots.csv; h08s_template.json; gather arrays (npz) for the shot-gather and
  residual-gather plots.
PROVENANCE: impact PDF = stand-in from run no-exhaustion-prior (b3dd44b), prior track 295.66 +- 1.0 deg.
Usage: python h08s_shot_template.py <kadri data dir> <stand-in summary json> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import h08s_pulse_energy as PE  # noqa: E402
import h08s_shot_outliers as H  # noqa: E402
import kadri_table1_test as KT  # noqa: E402
import kadri_trace_pairs as T  # noqa: E402

W0, W1 = -3.0, 6.0
WIN = {"pre": (-3.0, -1.0), "peak": (-1.0, 1.0), "post": (1.0, 4.0), "tail": (4.0, 6.0)}
SNRS_T = [-20, -15, -10, -6, -3, 0, 3]
HALF = 6
NPC = 3


def rz(x):
    x = np.asarray(x, float)
    return (x - np.nanmedian(x)) / (1.4826 * np.nanmedian(np.abs(x - np.nanmedian(x))))


def analyse(tg, p):
    k = int(0.25 * H.FS)
    env = np.log10(np.maximum(np.convolve(p ** 2, np.ones(k) / k, "same"), 1e-12))
    pu = PE.pulses(tg, p)
    shots = pu[np.nan_to_num(pu.z_E_peak.values, nan=0.0) > -3].reset_index(drop=True)
    n0, n1 = int(W0 * H.FS), int(W1 * H.FS)
    rel = np.arange(n0, n1) / H.FS
    keep, G = [], []
    for i, t in enumerate(shots.t.values):
        j = int(round((t - tg[0]) * H.FS))
        if j + n0 - 20 < 0 or j + n1 + 20 > len(env):
            continue
        keep.append(i)
        G.append(env[j + n0 - 20: j + n1 + 20])
    shots = shots.iloc[keep].reset_index(drop=True)
    G = np.array(G)
    ref = np.median(G[:, 20:-20], axis=0)
    A = np.zeros((len(G), n1 - n0))
    for i, g in enumerate(G):
        best = max(range(-20, 21), key=lambda s: np.corrcoef(g[20 + s: 20 + s + (n1 - n0)], ref)[0, 1])
        A[i] = g[20 + best: 20 + best + (n1 - n0)]
    An = A - A.mean(1, keepdims=True)
    rows = []
    for i in range(len(A)):
        nb = [j for j in range(max(0, i - HALF), min(len(A), i + HALF + 1)) if j != i]
        tmpl = np.median(An[nb], axis=0)
        pk = (rel >= -1) & (rel < 1)
        tmpl_abs = tmpl - tmpl[pk].mean() + A[i][pk].mean()
        r = dict(t=float(shots.t.iloc[i]), rho=float(np.corrcoef(An[i], tmpl)[0, 1]))
        for w, (a, b) in WIN.items():
            m = (rel >= a) & (rel < b)
            r[f"res_{w}_db"] = float(10 * (A[i][m].mean() - tmpl_abs[m].mean()))
        rows.append(r)
    S = pd.DataFrame(rows)
    U, s, Vt = np.linalg.svd(An - An.mean(0), full_matrices=False)
    rec = (U[:, :NPC] * s[:NPC]) @ Vt[:NPC]
    S["spe"] = ((An - An.mean(0) - rec) ** 2).sum(1)
    S["z_rho"] = rz(S.rho)
    for w in WIN:
        S[f"z_res_{w}"] = rz(S[f"res_{w}_db"])
    S["z_spe"] = rz(S.spe)
    return S, A, An, rel, float(np.median(shots.E_peak))


def flags(S):
    out = {"shape": S.z_rho.values <= -3, "spe": S.z_spe.values >= 3}
    for w in [w for w in WIN if w != "peak"]:           # 'peak' residual is zero by construction (DEFECT DISCLOSED)
        out[f"res_{w}_high"] = S[f"z_res_{w}"].values >= 3
        out[f"res_{w}_low"] = S[f"z_res_{w}"].values <= -3
    return out


def main(kd, summary, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    _bf, _cache = H.scorer(summary), {}

    def l10bf(a, b, bear=None):
        key = (round(a, 3), round(b, 3), bear)
        if key not in _cache:
            _cache[key] = _bf(a, b, bear)
        return _cache[key]
    h01 = {}
    for op, ratio in T.RATIOS.items():
        ts = []
        for pnl in "abc":
            t, s = T.triggers(kd, pnl, ratio)
            ts.append(t[(t >= s[0]) & (t <= s[1])])
        h01[op] = [(a, None) for a in np.concatenate(ts)]
    tab = pd.read_csv(kd / "kadri-table1-transients.csv")
    tab["t_s"] = [KT.secs(x) for x in tab.time_utc]
    g = tab[(tab.bearing_deg >= 246.03) & (tab.bearing_deg <= 284.25)]
    h01["table1_gated"] = [(r.t_s, r.bearing_deg) for r in g.itertuples()]
    ser, Ss, gathers = {}, [], {}
    for pnl in "de":
        tg, p = H.load(kd, pnl)
        S, A, An, rel, med = analyse(tg, p)
        S["panel"] = pnl
        ser[pnl] = (tg, p, med)
        Ss.append(S)
        gathers[f"A_{pnl}"], gathers[f"t_{pnl}"] = A, S.t.values
    gathers["rel"] = rel
    np.savez(out / "h08s_gathers.npz", **gathers)
    C = pd.concat(Ss, ignore_index=True)
    n = len(C)
    F = {}
    for pnl in "de":
        for k, v in flags(C[C.panel == pnl]).items():
            F.setdefault(k, []).append(v)
    F = {k: np.concatenate(v) for k, v in F.items()}
    res, sweep, outl = {}, [], []
    for k, flag in F.items():
        for v, h in h01.items():
            for thr in PE.BF_SWEEP:
                obs = sum(PE.coincident_thr(C.t.values[i], h, l10bf, thr) for i in np.flatnonzero(flag))
                nl = np.array([sum(PE.coincident_thr(C.t.values[i], h, l10bf, thr) for i in np.flatnonzero(np.roll(flag, s))) for s in range(1, n)])
                p = float((1 + (nl >= obs).sum()) / n)
                row = dict(statistic=k, h01w=v, log10_bf_min=thr, n_outliers=int(flag.sum()), n_coincident=int(obs), null_mean=float(nl.mean()), p=p)
                sweep.append(row)
                if thr == 1.0:
                    res[f"{k}|{v}"] = row | {"reading": "candidate: more coincidences than chance" if p < 0.05 else "consistent with chance"}
        for i in np.flatnonzero(flag):
            outl.append(dict(statistic=k, panel=C.panel.iloc[i], t_s=float(C.t.iloc[i]), t_utc=str(KT.DAY0 + pd.Timedelta(seconds=float(C.t.iloc[i])))[11:21]))
    tm = H.template()
    e2 = np.convolve(tm ** 2, np.ones(int(2 * H.FS)), "valid").max() / H.FS
    tmax = int(np.argmax(np.convolve(tm ** 2, np.ones(int(0.5 * H.FS)), "same")))
    rng = np.random.default_rng(H.SEED)
    pdr = []
    for snr in SNRS_T:
        hit = 0
        for _ in range(H.N_INJ):
            pnl = rng.choice(["d", "e"])
            tg, p, med = ser[pnl]
            gn = np.sqrt(10 ** (snr / 10) * med / e2)
            i0 = int(rng.uniform(20 * H.FS, len(tg) - len(tm) - 20 * H.FS))
            x = p.copy()
            x[i0: i0 + len(tm)] += gn * tm
            tinj = tg[i0 + tmax]
            S1, *_ = analyse(tg, x)
            j = np.flatnonzero((S1.t.values + W0 <= tinj) & (S1.t.values + W1 > tinj))
            if len(j) and any(v[j].any() for v in flags(S1).values()):
                hit += 1
        pdr.append(dict(snr_vs_median_shot_db=snr, pd=hit / H.N_INJ))
    summ = dict(n_shots=int(n), shots_per_panel=C.groupby("panel").size().to_dict(), rho_median=float(C.rho.median()),
                results=res, injection_pd=pdr, provenance="stand-in prior, run no-exhaustion-prior (b3dd44b), track 295.66 +- 1.0 deg; Kadri Fig 9 vectors")
    (out / "h08s_template.json").write_text(json.dumps(summ, indent=1, default=str))
    pd.DataFrame(sweep).to_csv(out / "h08s_template_bf_sweep.csv", index=False)
    C.to_csv(out / "h08s_template_shots.csv", index=False)
    pd.DataFrame(outl).to_csv(out / "h08s_template_outliers.csv", index=False)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
