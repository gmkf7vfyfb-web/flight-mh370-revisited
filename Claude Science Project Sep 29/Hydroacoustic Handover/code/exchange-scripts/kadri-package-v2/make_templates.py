"""Kadri package v2: export the module's M1b envelope templates and the run J pulse model in a self-contained form.
Source: the weak-signal track's KRAKEN broadband synthesis (prepare/weak_signal/template.py, bank.py; pre-registration
78c7e88): one range-independent WOA23 March profile at the representative H01W path midpoint (36.6 S 102.2 E), flat
bottom 4,610 m, receiver 1,200 m (channel axis), source 10 m, 2-48 Hz, 64 s window; the 'h2' convention (energy builds
to an abrupt end). The one-pole source spectrum (ESD flat to 1/tau, f^-2 above) is applied per tau, then the 5-40 Hz
band-pass; envelopes are 0.5 s-smoothed squared series at 10 Hz, 50 s long, zero-mean, unit energy, energy peak at 35 s.
Bank: ranges {1800, 2000, 2200, 2400, 2600, 2800, 3000, 3703.5 (H08S)} km x tau {0.1, 1, tau_runJ, 10} s, where tau_runJ is
the run J pooled median tau90 (predictions_meta.json; 2.9-3.2 s). Also writes the WAVEFORM pulse at 2,200 km (H01W range)
and tau_runJ at 250 Hz, unit energy, for synth_triad.py ("run J pulse model").
Writes templates_envelope.npz (+ .csv for inspection) and pulse_runj.npz. Caveat: model-matched templates on a flat
profile; range-dependent templates at the receiver depth are the module's planned upgrade (weak-signal note section 7).
Usage: python make_templates.py <templates_raw.npz> <predictions_meta.json> <out_dir>
"""
import json, pathlib, sys
import numpy as np
from scipy import signal

TLEN, PEAK_AT, BAND, ENV_FS = 50.0, 35.0, (5.0, 40.0), 10.0
RANGES = [1800.0, 2000.0, 2200.0, 2400.0, 2600.0, 2800.0, 3000.0, 3703.5]
PULSE_FS = 250.0


def source_filter(x, fs, tau):
    b, a = signal.butter(1, 1.0 / tau, btype="low", fs=fs)
    return signal.lfilter(b, a, x)


def pulse(T, r, tau, fs_out):
    h = T[f"h2_{r:.1f}"]; fs0 = float(T["fs"])
    e = np.convolve(h ** 2, np.ones(int(fs0)) / fs0, "same"); pk = int(np.argmax(e))
    h = np.roll(h, int(PEAK_AT * fs0) - pk)[: int(TLEN * fs0)]
    x = source_filter(h, fs0, tau)
    sos = signal.butter(4, list(BAND), btype="bandpass", fs=fs0, output="sos"); x = signal.sosfiltfilt(sos, x)
    from fractions import Fraction
    fr = Fraction(fs_out / fs0).limit_denominator(1000)
    x = signal.resample_poly(x, fr.numerator, fr.denominator)
    return (x / np.sqrt(np.sum(x ** 2))).astype(float)


def envelope(x, fs, smooth_s=0.5, out_fs=ENV_FS):
    e = x ** 2; k = max(int(smooth_s * fs), 1); e = np.convolve(e, np.ones(k) / k, "same")
    d = int(round(fs / out_fs)); n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)


def main(raw, meta, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    T = np.load(raw); tau_j = float(json.loads(pathlib.Path(meta).read_text())["pooled_medians"]["tau90_s"])
    taus = [0.1, 1.0, round(tau_j, 2), 10.0]
    env, keys = [], []
    for r in RANGES:
        for tau in taus:
            p = pulse(T, r, tau, 100.0)
            e = envelope(p, 100.0); e = e - e.mean(); env.append(e / np.sqrt(np.sum(e ** 2))); keys.append((r, tau))
    env = np.array(env)
    np.savez(out / "templates_envelope.npz", env=env, peak_idx=int(PEAK_AT * ENV_FS), fs=ENV_FS,
             ranges_km=np.array([k[0] for k in keys]), taus_s=np.array([k[1] for k in keys]),
             note=np.array("M1b envelope templates, 10 Hz, 50 s, zero-mean unit-energy; KRAKEN flat-profile synthesis (module 78c7e88); model-matched; C1 C2"))
    with open(out / "templates_envelope.csv", "w") as f:
        f.write("# M1b envelope templates (10 Hz, 50 s, zero-mean, unit energy); columns t_s then one column per (range_km, tau_s)\n")
        f.write("t_s," + ",".join(f"r{k[0]:g}_tau{k[1]:g}" for k in keys) + "\n")
        for i in range(env.shape[1]):
            f.write(f"{i / ENV_FS:.1f}," + ",".join(f"{v:.6e}" for v in env[:, i]) + "\n")
    pj = pulse(T, 2200.0, tau_j, PULSE_FS)
    np.savez(out / "pulse_runj.npz", x=pj, fs=PULSE_FS, range_km=2200.0, tau_s=tau_j,
             note=np.array("run J pulse model: KRAKEN deep-channel arrival at 2,200 km (H01W range), one-pole source tau = run J pooled median tau90, 5-40 Hz, unit energy, 250 Hz"))
    # per-template duration summary (seconds holding 90 % of the envelope energy)
    rows = []
    for (r, tau), e in zip(keys, env):
        c = np.cumsum(np.maximum(e, 0) ** 2); c /= c[-1]; rows.append((r, tau, float((np.searchsorted(c, 0.95) - np.searchsorted(c, 0.05)) / ENV_FS)))
    json.dump(dict(ranges_km=RANGES, taus_s=taus, tau_runj_s=tau_j, n_templates=len(keys), env_len_s=TLEN, peak_at_s=PEAK_AT,
                   env_90pct_span_s={f"r{r:g}_tau{t:g}": s for r, t, s in rows},
                   source="run-j-weak-signal/templates/templates_raw.npz (weak-signal track, 22 Oct 2026)"), open(out / "templates_meta.json", "w"), indent=1)
    print(len(keys), "templates; tau_runj", tau_j)


if __name__ == "__main__":
    main(*sys.argv[1:4])
