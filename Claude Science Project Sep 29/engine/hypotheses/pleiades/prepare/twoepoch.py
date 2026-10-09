"""Two-epoch (COSMO-SkyMed -> Pleiades) windage calibration by exhaustive matching enumeration.

PROVISIONAL. Brief section 6, the 9 Oct cosmo-pass ruling, and the D5 machinery (information gain in
bits, Bayes factor, injection-recovery).

Model, all of it declared:
  theta = (c_wind, cosmo-pass, pass offset, K)
    c_wind     windage on the export grid 0..5 % (0.25 % steps), prior uniform (prior work's 0-5 %)
    cosmo-pass dawn-20Mar / dusk-21Mar, prior 0.5 / 0.5 (ruling: equal unless a source says otherwise)
    offset     -25 / 0 / +25 min, Gauss-like weights 1/4, 1/2, 1/4
    K          log-uniform 30-1000 m2/s (the shared provisional prior), 8-node quadrature in ln K;
               ONE K per realisation, shared by every pair
  Deterministic track X_i(theta) from data/cosmo-tracks.csv (mh370-ocean, GLORYS12 + c_wind * ERA5,
  Stokes absorbed in c_wind, leeway angle 0). Analytic spread per component, in km^2:
    var = 2 K dt + var_OU(sigma_e, T_e, dt) + sd_cosmo^2 + sd_target^2
    var_OU = 2 sigma_e^2 T_e [dt - T_e (1 - exp(-dt/T_e))]   (model error with decorrelation T_e)
  The model-error part is either independent between pairs (reference) or fully SHARED by all pairs
  (one realisation; the conservative arm), never per-particle noise.
  Assignment a: partial injective map contacts -> targets. Prior
    P(a) proportional to prod_{i matched} pi_m w_{a(i)} * prod_{i unmatched} (1 - pi_m),
  w_t = the target's prior weight (rating weight, cluster-weight form). Likelihood ratio against
  every target being background (uniform over its scene, q = 1/A_scene, A_scene = 500 km2 from GA,
  "each scene is approximately 25 km x 20 km"):
    L(a | theta) = prod over matched pairs of [p(y_t | x_i, theta) * A_scene], joint over pairs.
  The empty assignment contributes 1 for every theta, which is how 'no information' stays possible.

Reported (always all of them): windage posterior marginalised over pass time; per pass; P(pass | D);
information gain in bits (KL posterior || prior on c_wind); Bayes factor of free windage against
windage fixed at the prior mean (2.5 %); P(at least one match | D); the leading assignments.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

KM_PER_DEG = 6371.0088 * math.pi / 180.0
A_SCENE_KM2 = 500.0
PASSES = ["dawn-20Mar", "dusk-21Mar"]
OFFSETS = [-1500, 0, 1500]
OFFSET_W = np.array([0.25, 0.5, 0.25])
PLEIADES_T = {"PHR_4": 1395548640.0, "PHR_2": 1395548640.0, "PHR_1": 1395548880.0, "PHR_3": 1395548880.0}
PASS_T = {"dawn-20Mar": 1395359760.0, "dusk-21Mar": 1395402960.0}
PRIOR_MEAN_C = 0.025


def k_nodes(n=8, kmin=30.0, kmax=1000.0):
    if kmin == kmax:
        return np.array([kmin]), np.array([1.0])
    x, w = np.polynomial.legendre.leggauss(n)
    lnk = 0.5 * (math.log(kmax) - math.log(kmin)) * x + 0.5 * (math.log(kmax) + math.log(kmin))
    return np.exp(lnk), w / w.sum()


def var_ou_km2(sigma_e_ms, T_e_s, dt_s):
    if sigma_e_ms == 0:
        return 0.0
    return 2 * sigma_e_ms**2 * T_e_s * (dt_s - T_e_s * (1 - math.exp(-dt_s / T_e_s))) / 1e6


@dataclass
class Config:
    sigma_e_ms: float = 0.05
    T_e_s: float = 2 * 86400.0
    sd_cosmo_km: float = 1.0
    sd_target_km: float = 0.5
    pi_match: float = 0.5
    shared_error: bool = False
    pass_prior: tuple = (0.5, 0.5)
    k_n: int = 8
    k_range: tuple = (30.0, 1000.0)
    label: str = "reference"

    def describe(self):
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class Tracks:
    """X[contact, pass, offset, c, scene_time] -> (lon, lat)."""
    contacts: list
    c: np.ndarray
    times: np.ndarray
    X: np.ndarray  # shape (n_contacts, 2 passes, 3 offsets, n_c, n_times, 2)

    @classmethod
    def load(cls, path: Path):
        d = pd.read_csv(path)
        contacts = sorted(d.contact.unique())
        c = np.sort(d.c_wind.unique())
        times = np.sort(d.out_unix_s.unique())
        X = np.full((len(contacts), 2, 3, len(c), len(times), 2), np.nan)
        ci = {v: i for i, v in enumerate(contacts)}
        cc = {round(v, 6): i for i, v in enumerate(c)}
        ti = {v: i for i, v in enumerate(times)}
        pi = {p: i for i, p in enumerate(PASSES)}
        oi = {o: i for i, o in enumerate(OFFSETS)}
        idx = (d.contact.map(ci), d["pass"].map(pi), d.offset_s.map(oi), d.c_wind.round(6).map(cc), d.out_unix_s.map(ti))
        X[idx[0], idx[1], idx[2], idx[3], idx[4], 0] = d.longitude
        X[idx[0], idx[1], idx[2], idx[3], idx[4], 1] = d.latitude
        assert np.isfinite(X).all(), "missing track entries"
        return cls(contacts, c, times, X)

    def at(self, contacts, scene_times):
        """Positions for the chosen contacts at each target's scene time: (nC, 2, 3, n_c, nT, 2)."""
        ii = [self.contacts.index(x) for x in contacts]
        tj = [int(np.argmin(np.abs(self.times - t))) for t in scene_times]
        return self.X[np.ix_(ii, [0, 1], [0, 1, 2], range(len(self.c)), tj, [0, 1])]


def assignments(n_contacts, n_targets):
    """All partial injective maps, as tuples of target index or -1 (unmatched), per contact."""
    out = []
    opts = list(range(n_targets))
    for matched in itertools.product([False, True], repeat=n_contacts):
        k = sum(matched)
        for perm in itertools.permutations(opts, k):
            a, it = [], iter(perm)
            for m in matched:
                a.append(next(it) if m else -1)
            out.append(tuple(a))
    return out


def n_assignments(m, n):
    return sum(math.comb(m, k) * math.perm(n, k) for k in range(min(m, n) + 1))


def offsets_km(Xc, targets):
    """Residual east/north (km) between targets and tracks: Xc (nC,2,3,nc,nT,2); targets (nT,2) lon,lat."""
    lon, lat = Xc[..., 0], Xc[..., 1]
    ylon, ylat = targets[:, 0], targets[:, 1]
    coslat = np.cos(np.radians(0.5 * (lat + ylat)))
    de = (ylon - lon) * coslat * KM_PER_DEG
    dn = (ylat - lat) * KM_PER_DEG
    return de, dn  # each (nC, 2, 3, nc, nT)


def analyse(tracks: Tracks, contacts, targets: pd.DataFrame, cfg: Config, pass_fixed=None, keep_top=5):
    """Posterior over theta, marginalised over every assignment. targets: columns lon, lat, scene, w."""
    T = targets[["lon", "lat"]].to_numpy()
    tt = np.array([PLEIADES_T[s] for s in targets.scene])
    w = targets.w.to_numpy(float)
    Xc = tracks.at(contacts, tt)
    de, dn = offsets_km(Xc, T)  # (nC,2,3,nc,nT)
    nC, nT = len(contacts), len(T)
    Ks, Kw = k_nodes(cfg.k_n, *cfg.k_range)
    dt = np.array([[tt[t] - (PASS_T[p] + o) for t in range(nT)] for p in PASSES for o in OFFSETS]).reshape(2, 3, nT)
    ou = np.vectorize(lambda x: var_ou_km2(cfg.sigma_e_ms, cfg.T_e_s, x))(dt)  # (2,3,nT)
    base = cfg.sd_cosmo_km**2 + cfg.sd_target_km**2
    A = assignments(nC, nT)
    # prior over assignments
    lp_a = np.array([sum(math.log(cfg.pi_match * w[t]) if t >= 0 else math.log(1 - cfg.pi_match) for t in a) for a in A])
    lp_a -= np.logaddexp.reduce(lp_a)
    nc = len(tracks.c)
    # log L(a | theta) for every assignment, theta = (pass, offset, c, K)
    logL = np.zeros((len(A), 2, 3, nc, len(Ks)))
    for ai, a in enumerate(A):
        pairs = [(i, t) for i, t in enumerate(a) if t >= 0]
        if not pairs:
            continue
        ii = [p[0] for p in pairs]
        jj = [p[1] for p in pairs]
        e = de[ii, :, :, :, jj]  # (m,2,3,nc)
        n = dn[ii, :, :, :, jj]
        m = len(pairs)
        for kk, K in enumerate(Ks):
            dif = 2 * K * dt[:, :, jj] / 1e6  # (2,3,m) km2
            if not cfg.shared_error:
                v = (dif + ou[:, :, jj] + base)  # (2,3,m)
                v = np.moveaxis(v, -1, 0)[..., None]  # (m,2,3,1)
                ll = -(e**2 + n**2) / (2 * v) - np.log(2 * np.pi * v)
                logL[ai, :, :, :, kk] = ll.sum(0) + m * math.log(A_SCENE_KM2)
            else:
                # cov = D + s 1 1^T per component; s = shared OU variance (mean over pairs' dt)
                D = np.moveaxis(dif + base + 0 * ou[:, :, jj], -1, 0)[..., None]  # (m,2,3,1)
                s = ou[:, :, jj].mean(-1)[..., None]  # (2,3,1)
                inv = 1 / D
                denom = 1 + s * inv.sum(0)
                logdet = np.log(D).sum(0) + np.log(denom)
                for comp in (e, n):
                    q = (comp**2 * inv).sum(0) - s * ((comp * inv).sum(0)) ** 2 / denom
                    logL[ai, :, :, :, kk] += -0.5 * q - 0.5 * logdet - 0.5 * m * math.log(2 * np.pi)
                logL[ai, :, :, :, kk] += m * math.log(A_SCENE_KM2)
    lpass = np.log(np.array(cfg.pass_prior))
    if pass_fixed is not None:
        lpass = np.full(2, -np.inf)
        lpass[PASSES.index(pass_fixed)] = 0.0
    lprior = (lpass[:, None, None, None] + np.log(OFFSET_W)[None, :, None, None]
              + np.full(nc, -math.log(nc))[None, None, :, None] + np.log(Kw)[None, None, None, :])
    lj = logL + lp_a[:, None, None, None, None] + lprior[None]
    lz = np.logaddexp.reduce(lj.reshape(-1))
    post_theta = np.exp(np.logaddexp.reduce(lj, axis=0) - lz)  # (2,3,nc,K)
    post_c = post_theta.sum((0, 1, 3))
    post_c_pass = post_theta.sum((1, 3))
    p_pass = post_c_pass.sum(1)
    post_c_given_pass = post_c_pass / np.where(p_pass[:, None] > 0, p_pass[:, None], 1)
    prior_c = np.full(nc, 1 / nc)
    ig = float(np.sum(post_c[post_c > 0] * np.log2(post_c[post_c > 0] / prior_c[post_c > 0])))
    ig_pass = [float(np.sum(q[q > 0] * np.log2(q[q > 0] / prior_c[q > 0]))) for q in post_c_given_pass]
    # Bayes factor: free windage vs fixed at the prior mean
    ic = int(np.argmin(np.abs(tracks.c - PRIOR_MEAN_C)))
    lz_c = np.logaddexp.reduce(np.moveaxis(lj, 3, 0).reshape(nc, -1), axis=1)  # ln p(D, c) incl. uniform 1/nc
    ln_bf = float(lz - (lz_c[ic] + math.log(nc)))
    p_any = 1 - float(np.exp(np.logaddexp.reduce(lj[0].reshape(-1)) - lz))
    post_a = np.exp(np.logaddexp.reduce(lj.reshape(len(A), -1), axis=1) - lz)
    top = [(A[i], float(post_a[i])) for i in np.argsort(-post_a)[:keep_top]]
    mean_c = float((post_c * tracks.c).sum())
    cdf = np.cumsum(post_c)
    q = lambda p: float(np.interp(p, cdf, tracks.c))
    return dict(post_c=post_c, post_c_given_pass=post_c_given_pass, p_pass=p_pass, ig_bits=ig, ig_bits_pass=ig_pass,
                ln_bf_free_vs_fixed=ln_bf, p_any_match=p_any, top=top, mean_c=mean_c, ci68=(q(0.16), q(0.84)),
                ci90=(q(0.05), q(0.95)), n_assign=len(A), lnZ=float(lz))
