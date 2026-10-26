"""Empirical triplet calibration from catalogue-matched T-phases (exploratory).
Model: measured inter-element lags = s(true back-azimuth, c) . (r_i - r_j + dr_i - dr_j) + (dt_i - dt_j), with
element 1 as reference (dr_1 = 0, dt_1 = 0); unknowns c, dt_2, dt_3, dr_2 (E,N), dr_3 (E,N): 7 parameters.
True back-azimuth = WGS84 geodesic azimuth from the FDSN triplet centroid to the catalogue epicentre.
Robust least squares (soft L1, f_scale 5 ms). Lags are rebuilt from the stored plane-wave fit (closure ~0)."""
import numpy as np
from scipy.optimize import least_squares
import ims_proc as P

def _lags(baz, v, xy):
    u = np.c_[np.sin(np.radians(baz)), np.cos(np.radians(baz))]; s = -u / (v[:, None] * 1000)
    D = np.array([xy[0] - xy[1], xy[1] - xy[2], xy[2] - xy[0]]); return s @ D.T, D

def _pairs(a):
    return np.stack([a[..., 0] - a[..., 1], a[..., 1] - a[..., 2], a[..., 2] - a[..., 0]], -1)

def fit(st, baz, v, baz_true):
    xy = P.enu([f"{st}{i}" for i in (1, 2, 3)]); L, D = _lags(baz, v, xy)
    up = np.c_[np.sin(np.radians(baz_true)), np.cos(np.radians(baz_true))]
    def pred(p):
        s = -up / (p[0] * 1000); dt = np.r_[0, p[1], p[2]]; dr = np.array([[0, 0], [p[3], p[4]], [p[5], p[6]]])
        Dp = D + np.array([dr[0] - dr[1], dr[1] - dr[2], dr[2] - dr[0]])
        return s @ Dp.T + np.array([dt[0] - dt[1], dt[1] - dt[2], dt[2] - dt[0]])
    r = least_squares(lambda p: (pred(p) - L).ravel(), [1.48, 0, 0, 0, 0, 0, 0], loss="soft_l1", f_scale=0.005)
    return r.x

def apply(st, baz, v, p):
    xy = P.enu([f"{st}{i}" for i in (1, 2, 3)]); L, D = _lags(baz, v, xy)
    dt = np.r_[0, p[1], p[2]]; dr = np.array([[0, 0], [p[3], p[4]], [p[5], p[6]]])
    L = L - np.array([dt[0] - dt[1], dt[1] - dt[2], dt[2] - dt[0]])
    Dp = D + np.array([dr[0] - dr[1], dr[1] - dr[2], dr[2] - dr[0]])
    s = np.linalg.lstsq(Dp, L.T, rcond=None)[0].T
    return np.degrees(np.arctan2(-s[:, 0], -s[:, 1])) % 360, 1 / np.linalg.norm(s, axis=1) / 1000
