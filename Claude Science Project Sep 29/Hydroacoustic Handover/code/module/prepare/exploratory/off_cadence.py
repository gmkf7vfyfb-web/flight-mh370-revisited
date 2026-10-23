"""EXPLORATORY (9 Oct; not pre-registered): prominent H08S pulses OFF the 9.98 s shot cadence. Complements
h08s_shot_outliers.py, whose injection test showed loud arrivals break the cycle structure. Peaks: envelope
maxima >= 3 s apart, prominence >= 2 x panel median envelope. Grid: per panel, T = median spacing of 9-11 s
intervals, phase = circular median of peak times mod T. Off-cadence: phase distance > 2 s from the grid.
Coincidence with H01W as h08s_shot_outliers (span + log10 BF >= 1); null = circular slides of the off-cadence
times over the H08S span (1 s steps). Injection: T_C2 at SNR_gap in {0..25} dB; detected if an off-cadence
peak lies within 2 s of the injection maximum."""
import sys, json, numpy as np, pandas as pd
from pathlib import Path
from scipy import signal
sys.path.insert(0, sys.argv[1]); import h08s_shot_outliers as H, kadri_trace_pairs as T, kadri_table1_test as KT
kd, out = Path(sys.argv[2]), Path(sys.argv[3])
def off(tg, p):
    k = int(0.5 * H.FS); env = np.convolve(p ** 2, np.ones(k) / k, "same")
    pk, _ = signal.find_peaks(env, distance=int(3 * H.FS), prominence=2 * np.median(env)); t = tg[pk]
    d = np.diff(t); per = float(np.median(d[(d >= 9) & (d <= 11)]))
    ph = np.angle(np.mean(np.exp(2j * np.pi * t / per))) * per / (2 * np.pi)
    dist = np.abs(((t - ph) / per - np.round((t - ph) / per)) * per)
    return t[dist > 2.0], per, env
l10bf = H.scorer("/tmp/nep.json")
h01 = {}
for op, ratio in T.RATIOS.items():
    ts = []
    for pnl in "abc":
        t, s = T.triggers(kd, pnl, ratio); ts.append(t[(t >= s[0]) & (t <= s[1])])
    h01[op] = [(a, None) for a in np.concatenate(ts)]
tab = pd.read_csv(kd / "kadri-table1-transients.csv"); tab["t_s"] = [KT.secs(x) for x in tab.time_utc]
g = tab[(tab.bearing_deg >= 246.03) & (tab.bearing_deg <= 284.25)]; h01["table1_gated"] = [(r.t_s, r.bearing_deg) for r in g.itertuples()]
ser, evs, spans = {}, [], []
for pnl in "de":
    tg, p = H.load(kd, pnl); e, per, _ = off(tg, p); ser[pnl] = (tg, p); evs.append(e); spans.append((tg[0] + 20, tg[-1] - 1))
E = np.concatenate(evs); L = sum(b - a for a, b in spans)
def to_u(t):
    o, off_ = [], 0.0
    for a, b in spans:
        m = (t >= a) & (t <= b); o.append(t[m] - a + off_); off_ += b - a
    return np.concatenate(o)
def from_u(u):
    o, off_ = [], 0.0
    for a, b in spans:
        m = (u >= off_) & (u < off_ + b - a); o.append(u[m] - off_ + a); off_ += b - a
    return np.concatenate(o)
res = {}
for v, h in h01.items():
    nobs = sum(H.coincident(t, h, l10bf) for t in E); u = to_u(E)
    nl = np.array([sum(H.coincident(t, h, l10bf) for t in from_u(np.mod(u + s, L))) for s in range(1, int(L), 2)])
    res[v] = dict(n_off_cadence=int(len(E)), n_coincident=int(nobs), null_mean=float(nl.mean()), p=float((1 + (nl >= nobs).sum()) / (1 + len(nl))))
tm = H.template(); w4 = int(4 * H.FS); e4 = np.convolve(tm ** 2, np.ones(w4), "valid").max() / H.FS
rng = np.random.default_rng(H.SEED); pdr = []
for snr in H.SNRS:
    hit = 0
    for _ in range(200):
        pnl = rng.choice(["d", "e"]); tg, p = ser[pnl]; c0, _, _ = H.cycles(tg, p); pg = float(np.median(c0.P_gap))
        gn = np.sqrt(10 ** (snr / 10) * pg * 4.0 / e4); i0 = int(rng.uniform(20 * H.FS, len(tg) - len(tm) - 20 * H.FS))
        x = p.copy(); x[i0:i0 + len(tm)] += gn * tm; tinj = tg[i0 + int(np.argmax(np.convolve(tm ** 2, np.ones(int(0.5 * H.FS)), "same")))]
        e1, _, _ = off(tg, x); hit += bool(np.any(np.abs(e1 - tinj) <= 2.0))
    pdr.append(dict(snr_gap_db=snr, pd=hit / 200))
summ = dict(off_cadence_utc=[str(KT.DAY0 + pd.Timedelta(seconds=float(t)))[11:19] for t in E], results=res, injection_pd=pdr)
(out / "off_cadence.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ, indent=1))
