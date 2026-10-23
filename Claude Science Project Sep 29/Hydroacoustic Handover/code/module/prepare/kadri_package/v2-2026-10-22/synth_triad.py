"""Synthetic triad waveforms for the reference-measurement self-test (package v2; run J pulse model).
A plane wave from back-azimuth BAZ at apparent speed C crosses the three H01W elements (data/stations.csv, 2014 epoch).
Source pulse: pulse_runj.npz = the module's KRAKEN deep-sound-channel arrival at 2,200 km (H01W range) with the one-pole
source spectrum at tau = run J pooled median tau90, band-passed 5-40 Hz (make_templates.py) - a MODEL pulse, not a
measurement; it is model-matched to the M1b templates, so the self-test is the best case. Amplitude A sets the in-pulse
RMS SNR (dB) against the 5-40 Hz band RMS of the noise. Noise: Gaussian with a -5 dB/octave spectrum between 1 and 60 Hz
(a stand-in for the low-frequency ambient slope; not any station's measured noise), independent per element, RMS sigma Pa
broadband. Output .npz in reference_measure.py's input format (float32 x). Duration 180 s, arrival at 100 s.
Usage: python synth_triad.py <out.npz> <baz_deg> <snr_db> [seed] [--pulse pulse_runj.npz] [--stations stations.csv]
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
from reference_measure import enu, bandpass  # noqa: E402

FS, DUR, T_ARR, C, SIGMA = 250.0, 180.0, 100.0, 1482.0, 0.05


def coloured_noise(rng, n, fs, sigma):
    w = rng.normal(0, 1, n); W = np.fft.rfft(w); f = np.fft.rfftfreq(n, 1 / fs)
    g = np.ones_like(f); m = f > 1.0
    g[m] = (f[m] / 1.0) ** (-5.0 / (20.0 * np.log10(2.0)))      # amplitude ~ f^-0.83: PSD slope -5 dB per octave above 1 Hz
    g[f > 60.0] *= np.exp(-(f[f > 60.0] - 60.0) / 10.0)
    x = np.fft.irfft(W * g, n)
    return x / x.std() * sigma


def make(baz, snr_db, seed=1, pulse_path=None, stations=None):
    here = Path(__file__).parent
    st = pd.read_csv(stations or here.parents[2] / "data/stations.csv", comment="#")
    e = st[st.triad == "H01W"].sort_values("element")
    xy = enu(e.latitude_deg.values, e.longitude_deg.values)
    k = -np.array([np.sin(np.radians(baz)), np.cos(np.radians(baz))])     # propagation direction (towards the receiver)
    P = np.load(pulse_path or here / "pulse_runj.npz"); p = P["x"].astype(float); fsp = float(P["fs"])
    assert abs(fsp - FS) < 1e-6
    tp = np.arange(len(p)) / FS
    tt = np.arange(int(DUR * FS)) / FS
    rng = np.random.default_rng(seed)
    x = np.stack([coloured_noise(rng, len(tt), FS, SIGMA) for _ in range(3)])
    nb = bandpass(x[0], FS, 5, 40).std()                                   # noise RMS in 5-40 Hz
    # in-pulse RMS: over the central 90 % energy span of the pulse
    c = np.cumsum(p ** 2) / np.sum(p ** 2); i0, i1 = np.searchsorted(c, 0.05), np.searchsorted(c, 0.95)
    prms = np.sqrt(np.mean(p[i0:i1] ** 2))
    a = nb * 10 ** (snr_db / 20) / prms
    for i in range(3):
        t0 = T_ARR + (xy[i] @ k) / C
        x[i] += a * np.interp(tt - t0, tp, p, left=0, right=0)
    return dict(t0_utc="2014-03-08T00:45:00", fs=FS, x=x.astype(np.float32), lat=e.latitude_deg.values, lon=e.longitude_deg.values,
                baz_true_deg=baz, snr_true_db=snr_db, t_arrival_s=T_ARR, pulse_span_s=np.array([tp[i0], tp[i1]]))


if __name__ == "__main__":
    args = sys.argv[1:]; pulse = None; stations = None
    if "--pulse" in args: k = args.index("--pulse"); pulse = args[k + 1]; del args[k:k + 2]
    if "--stations" in args: k = args.index("--stations"); stations = args[k + 1]; del args[k:k + 2]
    np.savez(args[0], **make(float(args[1]), float(args[2]), int(args[3]) if len(args) > 3 else 1, pulse, stations))
