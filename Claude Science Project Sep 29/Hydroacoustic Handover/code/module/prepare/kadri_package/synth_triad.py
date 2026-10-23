"""Synthetic triad waveforms for the reference-measurement self-test (DRAFT; brief section 9).
A plane wave from back-azimuth BAZ at apparent speed C crosses the three H01W elements (data/stations.csv,
2014 epoch). Source pulse: a 5-40 Hz linear down-chirp of 8 s (a stand-in for a dispersed SOFAR arrival,
NOT a model of any impact), Hann-tapered, amplitude A Pa, in white Gaussian noise of RMS sigma Pa,
independent per element. Writes an .npz in reference_measure.py's input format.
Usage: python synth_triad.py <out.npz> <baz_deg> <snr_db> [seed]"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
from reference_measure import enu  # noqa: E402

FS, DUR, T_ARR, C, SIGMA = 250.0, 300.0, 200.0, 1482.0, 0.05


def make(baz, snr_db, seed=1):
    st = pd.read_csv(Path(__file__).parents[2] / "data/stations.csv", comment="#")
    e = st[st.triad == "H01W"].sort_values("element")
    xy = enu(e.latitude_deg.values, e.longitude_deg.values)
    k = -np.array([np.sin(np.radians(baz)), np.cos(np.radians(baz))])     # propagation direction
    tt = np.arange(int(DUR * FS)) / FS
    tp = np.arange(int(8 * FS)) / FS
    pulse = signal.chirp(tp, 40, tp[-1], 5) * np.hanning(len(tp))
    a = SIGMA * 10 ** (snr_db / 20) / np.sqrt(np.mean(pulse ** 2))          # in-pulse RMS SNR vs broadband noise
    rng = np.random.default_rng(seed)
    x = rng.normal(0, SIGMA, (3, len(tt)))
    for i in range(3):
        t0 = T_ARR + (xy[i] @ k) / C
        x[i] += a * np.interp(tt - t0, tp, pulse, left=0, right=0)
    return dict(t0_utc="2014-03-08T00:45:00", fs=FS, x=x, lat=e.latitude_deg.values, lon=e.longitude_deg.values)


if __name__ == "__main__":
    np.savez(sys.argv[1], **make(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 1))
