"""Hand-computed fixtures for davey_ch11.py. Run: python -m pytest test_davey_ch11.py, or
python test_davey_ch11.py (plain asserts).

F1  eq. 11.9 on a 3-drifter toy. Starts A=(0,0) arrives, B=(0,0) does not, C=(10,0) does not;
    sigma = 1 deg, eps = 1e-4. With K0 = 1/(2 pi) = 0.1591549:
      at (0,0):  num = K0 / 1 = 0.1591549      den = (2 K0 + K0 e^-50) / 3 = 0.1061033
                 l = (0.1591549 + 1e-4) / (0.1061033 + 1e-4) = 1.4995290
      at (10,0): num = K0 e^-50 ~ 0              den = (K0 + 2 K0 e^-50) / 3 = 0.0530516
                 l = 1e-4 / (0.0530516 + 1e-4) = 0.0018814
    Checked for the exact KDE, and for the binned/filtered KDE to 0.5%.
F2  eps limits: eps -> infinity gives l -> 1; with eps = 0 the ratio at (0,0) is exactly 1.5.
F3  arrival bookkeeping: drifter 0 reaches R on elapsed day 500 -> arrival 1 un-joined;
    drifter 1 alone ends after 200 days -> 0 un-joined, 1 when joined (at day 135) to drifter 2,
    which passes the same point on the same day of year one year later and enters R 365 days
    after the join (elapsed 500).
F4  Kish ESS fraction: w = (1,1), l = (1,3) -> (4)^2 / (2 * 10) = 0.8.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import davey_ch11 as dc  # noqa: E402

K0 = 1.0 / (2.0 * np.pi)


def test_f1_exact_ratio():
    px, py, w = np.array([0.0, 0.0, 10.0]), np.zeros(3), np.array([1.0, 0.0, 0.0])
    x, y = np.array([0.0, 10.0]), np.zeros(2)
    num = dc.kde_exact(px, py, w, x, y, 1.0)
    den = dc.kde_exact(px, py, np.ones(3), x, y, 1.0)
    l = (num + 1e-4) / (den + 1e-4)
    assert abs(num[0] - 0.1591549) < 1e-6 and abs(den[0] - 0.1061033) < 1e-6
    assert abs(l[0] - 1.4995290) < 1e-6, l
    assert abs(l[1] - 0.0018814) < 1e-6, l


def test_f1_binned_matches_exact():
    cfg = dict(dc.CONFIG, BOX=(-20.0, 20.0, -20.0, 20.0), BIN_DEG=0.05)
    lat, lon, w = np.zeros(3), np.array([0.0, 0.0, 10.0]), np.array([1.0, 0.0, 0.0])
    l, num, den = dc.likelihood(lat, lon, w, np.array([0.0, 0.0]), np.array([0.0, 10.0]), cfg)
    assert abs(num[0] / 0.1591549 - 1) < 5e-3 and abs(den[0] / 0.1061033 - 1) < 5e-3, (num, den)
    assert abs(l[0] / 1.4995290 - 1) < 5e-3 and abs(l[1] / 0.0018814 - 1) < 5e-3, l


def test_f2_eps_limits():
    px, py = np.array([0.0, 0.0, 10.0]), np.zeros(3)
    num = dc.kde_exact(px, py, [1, 0, 0], [0.0], [0.0], 1.0)
    den = dc.kde_exact(px, py, [1, 1, 1], [0.0], [0.0], 1.0)
    assert abs(num[0] / den[0] - 1.5) < 1e-12
    assert abs((num[0] + 1e6) / (den[0] + 1e6) - 1.0) < 1e-6


def _toy_tracks():
    rlat, rlon = dc.REUNION
    d0 = np.arange(600)                              # drifter 0: day 0..599
    lat0 = np.where(d0 >= 500, rlat, -35.0); lon0 = np.where(d0 >= 500, rlon, 90.0)
    d1 = np.arange(200)                              # drifter 1: dies at day 199, at (-30, 80) from day 135
    lat1 = np.where(d1 >= 135, -30.0, -36.0); lon1 = np.where(d1 >= 135, 80.0, 95.0)
    d2 = np.arange(365 + 100, 365 + 700)             # drifter 2: at (-30, 80) on day 500 (= 135 + 365)
    lat2 = np.where(d2 >= 865, rlat, -30.0); lon2 = np.where(d2 >= 865, rlon, 80.0)
    day = np.r_[d0, d1, d2]
    drifter = np.r_[np.zeros(600, int), np.ones(200, int), 2 * np.ones(len(d2), int)]
    lat = np.r_[lat0, lat1, lat2]; lon = np.r_[lon0, lon1, lon2]
    return dc.Tracks(drifter, day + 16000, lat, lon)   # 16000 days ~ 2013-10-22 (any epoch works)


def test_f3_arrivals():
    tr = _toy_tracks()
    starts = np.array([0, 600])                      # first fix of drifter 0 and of drifter 1
    a1 = dc.simulate(tr, starts, n_mc=3, n_seg=1)
    assert np.allclose(a1, [1.0, 0.0]), a1
    a4 = dc.simulate(tr, starts, n_mc=3, n_seg=4)
    assert np.allclose(a4, [1.0, 1.0]), a4


def test_f4_ess():
    assert abs(dc.ess_fraction([1, 1], np.array([1.0, 3.0])) - 0.8) < 1e-12


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
