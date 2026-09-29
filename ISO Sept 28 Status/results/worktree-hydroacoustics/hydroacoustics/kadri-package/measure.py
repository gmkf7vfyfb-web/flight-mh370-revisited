"""Reference measurements of a transient on one hydrophone or a triad (numpy only).

The same code measures every arrival in our analysis and is the script sent to Usama Kadri,
so his numbers and ours are computed identically. Input is pressure in Pa, shape
(channels, samples), at `fs` Hz. For triads, give hydrophone positions in degrees.

For each band, over a signal window [t, t + duration] and a noise window ending `gap_s`
before t, it reports:
- peak_pa: the largest |p| on any channel in the signal window;
- rms_pa and exposure_pa2s: the channel mean of RMS and of the integral of p^2 over the window;
- noise_rms_pa: the RMS in the noise window;
- snr_db: 20 log10(rms_pa / noise_rms_pa).
Triads add a plane-wave fit to the cross-correlation lags: back-azimuth (degrees from north,
the direction the sound comes from), apparent speed and lag-closure residual.

Filters are zero-phase Butterworth: the |H|^2 response of forward-backward filtering, applied
by FFT. Measure away from record ends.
"""

from __future__ import annotations

import numpy as np

BANDS = ((2.0, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 40.0))


def butterworth_power(f, low, high, order=4):
    """|H(f)|^2 of an order-`order` Butterworth band-pass: the zero-phase (filtfilt) response."""
    af = np.maximum(np.abs(f), 1e-30)
    g = np.ones_like(af)
    if low:
        g /= 1.0 + (low / af) ** (2 * order)
    if high:
        g /= 1.0 + (af / high) ** (2 * order)
    return g


def bandpass(x, fs, low, high, order=4):
    n = x.shape[-1]
    return np.fft.irfft(np.fft.rfft(x, axis=-1) * butterworth_power(np.fft.rfftfreq(n, 1 / fs), low, high, order), n,
                        axis=-1)


def local_xy(lat, lon):
    """East and north offsets (m) of each hydrophone from their mean position."""
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    r = 6_371_000.0
    east = np.radians(lon - lon.mean()) * r * np.cos(np.radians(lat.mean()))
    north = np.radians(lat - lat.mean()) * r
    return np.column_stack([east, north])


def lag(a, b, fs):
    """Delay (s) of b relative to a from the cross-correlation peak, refined by a parabola."""
    n = a.size + b.size - 1
    size = 1 << (n - 1).bit_length()
    c = np.fft.irfft(np.conj(np.fft.rfft(a, size)) * np.fft.rfft(b, size), size)
    c = np.concatenate([c[-(a.size - 1):], c[: b.size]])  # lags -(len a - 1) .. len b - 1
    k = int(np.argmax(c))
    shift = 0.0
    if 0 < k < c.size - 1:
        denom = c[k - 1] - 2 * c[k] + c[k + 1]
        shift = 0.5 * (c[k - 1] - c[k + 1]) / denom if denom != 0 else 0.0
    return (k - (a.size - 1) + shift) / fs


def plane_wave(p, fs, xy):
    """Least-squares plane wave through the three pairwise lags: back-azimuth (deg), apparent
    speed (km/s) and closure residual (s) = lag12 + lag23 - lag13."""
    pairs = [(0, 1), (1, 2), (0, 2)]
    lags = np.array([lag(p[i], p[j], fs) for i, j in pairs])
    baseline = np.array([xy[j] - xy[i] for i, j in pairs])
    slowness, *_ = np.linalg.lstsq(baseline, lags, rcond=None)  # s/m, along the propagation direction
    back_azimuth = np.degrees(np.arctan2(-slowness[0], -slowness[1])) % 360
    speed = 1e-3 / np.hypot(*slowness) if np.any(slowness) else np.inf
    return back_azimuth, speed, lags[0] + lags[1] - lags[2]


def measure(p, fs, t, duration, noise_s=60.0, gap_s=10.0, lat=None, lon=None, bands=BANDS):
    """Measurements of the transient starting `t` seconds into `p` (one dict per band)."""
    p = np.atleast_2d(np.asarray(p, float))
    i, j = int(round(t * fs)), int(round((t + duration) * fs))
    k0, k1 = int(round((t - gap_s - noise_s) * fs)), int(round((t - gap_s) * fs))
    if k0 < 0 or j > p.shape[1]:
        raise ValueError("signal or noise window runs off the record")
    rows = []
    for low, high in bands:
        x = bandpass(p, fs, low, high)
        signal, noise = x[:, i:j], x[:, k0:k1]
        rms = np.sqrt((signal**2).mean(axis=1)).mean()
        noise_rms = np.sqrt((noise**2).mean(axis=1)).mean()
        row = {"band_hz": f"{low:g}-{high:g}", "peak_pa": np.abs(signal).max(), "rms_pa": rms,
               "exposure_pa2s": (signal**2).sum(axis=1).mean() / fs, "noise_rms_pa": noise_rms,
               "snr_db": 20 * np.log10(rms / noise_rms)}
        if p.shape[0] == 3 and lat is not None:
            row["back_azimuth_deg"], row["apparent_speed_km_s"], row["closure_s"] = plane_wave(
                signal, fs, local_xy(lat, lon))
        rows.append(row)
    return rows


def delay(x, fs, seconds):
    """Delay a signal by a fractional number of samples (circular, by FFT phase shift)."""
    f = np.fft.rfftfreq(x.shape[-1], 1 / fs)
    return np.fft.irfft(np.fft.rfft(x) * np.exp(-2j * np.pi * f * seconds), x.shape[-1])


def plane_wave_delays(lat, lon, back_azimuth_deg, speed_km_s=1.485):
    """Arrival time (s) at each hydrophone, relative to the array centre, of a plane wave coming
    from `back_azimuth_deg`."""
    theta = np.radians(back_azimuth_deg)
    towards = -np.array([np.sin(theta), np.cos(theta)])  # propagation direction (east, north)
    return local_xy(lat, lon) @ towards / (speed_km_s * 1e3)


def synthetic(fs, duration_s, exposure_db, rng):
    """The pre-registered injection waveform (preregistration.toml [injection]): 2-40 Hz Gaussian
    noise under a Hann envelope of `duration_s`, scaled to a broadband exposure (dB re 1 uPa^2 s)."""
    pad = int(10 * fs)
    n = int(round(duration_s * fs))
    x = bandpass(rng.standard_normal(n + 2 * pad), fs, 2.0, 40.0)[pad:pad + n] * np.hanning(n)
    return x * np.sqrt(10 ** (exposure_db / 10) * 1e-12 / ((x * x).sum() / fs))
