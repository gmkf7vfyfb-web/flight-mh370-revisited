"""IMOS raw-record I/O for the whale-call track (8 March 2014 records and the 14-day backgrounds).

Reading, calibration and clock handling copy the module's pre-registered chain
(code/module/prepare/imos_noise.py and imos_preregistration.py, branch claude-science-sep29):
  * big-endian uint16, 5 header lines, ASCII footer from 'Record'; volts = counts * 5 / 65536, mean removed;
  * logger start time = footer 'First Data-' time (logger clock);
  * UTC = logger time - e(t), e(t) linear between the two 'system clock set' entries (convention A, verified by the
    module clock test on the Curtin 01:33:44 control, dA = -0.24 s);
  * received level: dB re 1 uPa^2/Hz = 10 log10(V^2/Hz) - G(f) - S_h, G from the logger's white-noise calibration file
    (input -90 dB re 1 V^2/Hz), S_h the metadata sensitivity read as dB re 1 V^2/uPa^2.
    UNITS (deviation inherited from the module, imos_noise.py): the metadata label says 'dB re V^2/Pa^2', but the values
    (-196 to -197.8) are the magnitudes of an HTI-90-U class hydrophone re 1 V/uPa. Read literally (re Pa) every level
    would sit 120 dB above any measured ocean noise; with the uPa reading the 5-40 Hz record medians are 80-97 dB re 1 uPa^2/Hz,
    consistent with ambient noise. Detection does not depend on this constant (all detectors use relative levels).
Data are resampled to FS = 250 Hz (Nyquist 125 Hz covers fin-whale 96 Hz and Sri Lankan 105 Hz components).
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

IMOS = Path("/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos")
META = ["MH370/3315_3250_3376__MetaData.txt", "Portland_MH370/MetaData_3274_3275.txt"]
SETS = {"3315": "MH370/3315_PerthCanyon", "3376": "MH370/3376_PerthCanyon", "3250": "MH370/3250_ScottReef",
        "3274": "Portland_MH370/3274_Portland", "3275": "Portland_MH370/3275_Portland"}
SITE = {"3315": "Perth Canyon", "3376": "Perth Canyon", "3250": "Scott Reef", "3274": "Portland", "3275": "Portland"}
FS0, FS = 6000, 250
Q = FS0 // FS


def read_volts(path):
    raw = Path(path).read_bytes()
    pos = 0
    for _ in range(5):
        pos = raw.index(b"\n", pos) + 1
    tail = raw[-1000:]
    footer_bytes = 1000 - tail.index(b"Record")
    end = len(raw) - footer_bytes - 2
    n = (end - pos) // 2
    x = np.frombuffer(raw, dtype=">u2", count=n, offset=pos).astype(np.float64) * (5.0 / 65536)
    return x - x.mean(), raw[-1000:].decode("latin1")


def start_logger(tail_text):
    first = re.search(r"First Data-(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d)", tail_text).group(1)
    return pd.Timestamp(first.replace("/", "-"), tz="UTC")


def _dm(s):
    m = re.match(r"\s*(\d+)\s*deg\s*([\d.]+)'\s*([NSEW])", s)
    v = int(m.group(1)) + float(m.group(2)) / 60
    return -v if m.group(3) in "SW" else v


@lru_cache(None)
def parse_meta():
    out = {}
    for mf in META:
        txt = (IMOS / mf).read_text(errors="replace").replace("\r", "")
        for block in txt.split("Curtin ID")[1:]:
            lines = ("Curtin ID" + block).splitlines()
            kv = {ln[:40].strip(): ln[40:].strip() for ln in lines if len(ln) > 40}
            cid = kv["Curtin ID"]
            c1, c2 = kv["system clock set 1"].split(), kv["system clock set 2"].split()
            out[cid] = dict(lat=_dm(kv["Latitude (WGS84)"]), lon=_dm(kv["Longitude (WGS84)"]),
                            clock1=(pd.Timestamp(f"{c1[0]} {c1[1]}", tz="UTC"), float(c1[2])),
                            clock2=(pd.Timestamp(f"{c2[0]} {c2[1]}", tz="UTC"), float(c2[2])),
                            sens_db=float(kv["hydrophone sensitivity (dB re V^2/Pa^2)"]),
                            cal_file=kv["system gain file"].split()[-1])
    return out


def clock_err(cid, t):
    m = parse_meta()[cid]
    (t1, e1), (t2, e2) = m["clock1"], m["clock2"]
    return e1 + (e2 - e1) * (t - t1).total_seconds() / (t2 - t1).total_seconds()


def to_utc(cid, t_logger):
    """Convention A: true = logger - e(t)."""
    return t_logger - pd.Timedelta(seconds=clock_err(cid, t_logger))


def decimate(x):
    return signal.resample_poly(x, 1, Q)


@lru_cache(None)
def gain_curve(cid):
    """Returns (f, G dB) of the recorder chain from its white-noise calibration file (imos_noise.gain_db)."""
    cal = parse_meta()[cid]["cal_file"]
    p = next(IMOS.glob(f"*/*alibration/{cal}"))
    x, _ = read_volts(p)
    xd = signal.resample_poly(x, 1, 12)          # 500 Hz as in imos_noise
    f, pxx = signal.welch(xd, fs=500, window="hann", nperseg=2000, noverlap=1000, detrend="constant")
    return f, 10 * np.log10(pxx) + 90.0


def cal_db(cid, f):
    """dB to ADD to 10log10(V^2/Hz) to obtain dB re 1 uPa^2/Hz."""
    fg, G = gain_curve(cid)
    return -(np.interp(f, fg, G) + parse_meta()[cid]["sens_db"])


def load(cid, path):
    """Return dict(x=250 Hz volts, t0_logger, t0_utc, cid)."""
    x, tail = read_volts(path)
    t0 = start_logger(tail)
    return dict(x=decimate(x), t0_logger=t0, t0_utc=to_utc(cid, t0), cid=cid, file=str(path))


def spectrogram(x, nper, step, fs=FS, fmax=125.0):
    """Hann STFT power (V^2/Hz, one-sided). Returns f, t (s from record start, frame centre), P[f, t]."""
    f, t, S = signal.spectrogram(x, fs=fs, window="hann", nperseg=nper, noverlap=nper - step,
                                 detrend="constant", scaling="density", mode="psd")
    m = f <= fmax
    return f[m], t, S[m]
