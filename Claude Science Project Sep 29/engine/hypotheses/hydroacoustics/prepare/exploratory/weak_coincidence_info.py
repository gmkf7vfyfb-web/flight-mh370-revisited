"""EXPLORATORY planning analysis (9 Oct; not a test, no data examined). Information (bits, KL posterior||prior)
from a weak detection at H01W (+ H08S), as a function of pick sd, bearing sd and pi = P(the candidate is
the impact signal). Likelihood is the honest mixture L(x) = (1 - pi) p_bg + pi p_real(obs | x), with p_bg
uniform in arrival time over each station's +-1 h window and uniform in bearing. Prior, geometry and timing
model exactly as synthetic_composer_test.py (stand-in no-exhaustion-prior PDF, sigma_x 20 NM, mu_t 300 s,
sigma_t 180 s, c 1.482 +- 0.006 km/s, Student-t nu=3 bearings)."""
import sys, json, numpy as np
from math import lgamma, log, pi as PI
sys.path.insert(0, sys.argv[1]); import synthetic_composer_test as S
rng = np.random.default_rng(20261009)
ridge, grid, dens, _ = S.ridge_and_marginal(sys.argv[2]); q, _ = S.fit_small_circle(ridge)
pr = S.draw_prior(rng, q, grid, dens, 200_000, 20.0); geom = S.station_geometry(pr); N = len(pr)
W_T, NU, K = 7200.0, 3.0, 150
def lt(x, s): return lgamma((NU+1)/2) - lgamma(NU/2) - 0.5*log(NU*PI) - np.log(s) - (NU+1)/2*np.log1p((x/s)**2/NU)
def run(stations, pick, bsd, pis, spurious=False):
    out = {p: [] for p in pis}; m = len(stations); cfg = S.BASE
    for ti in rng.choice(N, K, replace=False):
        sd = np.array([np.hypot(pick, geom[s][0][ti]*S.SD_C_KM_S/S.C_KM_S**2) for s in stations])
        cov = np.diag(sd**2) + cfg["sigma_t_s"]**2*np.ones((m, m)); ci = np.linalg.inv(cov); _, ld = np.linalg.slogdet(2*PI*cov)
        pred = np.column_stack([geom[s][0]/S.C_KM_S for s in stations]) + cfg["mu_t_s"]
        if spurious:
            obs = pred[ti] + rng.uniform(-W_T/2, W_T/2, m)
        else:
            obs = cfg["mu_t_s"] + cfg["sigma_t_s"]*rng.normal() + np.array([geom[s][0][ti]/S.C_KM_S + sd[j]*rng.normal() for j, s in enumerate(stations)])
        r = obs[None, :] - pred
        ll = -0.5*np.einsum("ij,jk,ik->i", r, ci, r) - 0.5*ld
        lbg = -m*np.log(W_T)
        if bsd:
            sc = bsd/np.sqrt(NU/(NU-2))
            for s in stations:
                bt = rng.uniform(0, 360) if spurious else geom[s][1][ti] + sc*rng.standard_t(NU)
                ll = ll + lt(S.wrap180(bt - geom[s][1]), sc); lbg -= np.log(360.0)
        for p in pis:
            a = np.logaddexp(np.log1p(-p) + lbg if p < 1 else -np.inf, np.log(p) + ll)
            a -= a.max(); w = np.exp(a); w /= w.sum(); nz = w > 0
            out[p].append(float(np.sum(w[nz]*np.log2(w[nz]*N))))
    return {f"{p:g}": float(np.median(v)) for p, v in out.items()}
rows = []
PIS = [1.0, 0.5, 0.2, 0.05]
for st in [("H01W",), ("H01W", "H08S")]:
    for pick in [5.0, 10.0, 20.0, 40.0]:
        for bsd in [None, 3.3, 6.0, 12.0]:
            r = run(st, pick, bsd, PIS); s = run(st, pick, bsd, PIS, spurious=True)
            rows.append(dict(stations="+".join(st), pick_s=pick, bearing_sd_deg=bsd or 0.0, real_bits=r, spurious_bits=s))
            print("+".join(st), pick, bsd, "real", r, "spurious", s, flush=True)
json.dump(rows, open(sys.argv[3], "w"), indent=1)
