"""Tension statistic of the drift module, extracted unchanged from offline/smooth_stage2.py (lines 11-30) so that it can be called
on synthetic likelihood curves. Same latitude bins (0.1 degree, 40.25-19.9 S), same prior per unit arc length, same core (ruled final end-of-flight model, D0)."""
import numpy as np
from scipy import stats
Zl = np.load('arcm.npz'); l0 = Zl['D0|lat']; ok0 = np.isfinite(l0); l0 = l0[ok0]; pi0 = np.nan_to_num(Zl['D0|(uniform along the arc)'])[ok0]; ls_ = np.sort(l0[pi0 > 0])
cf = np.polyfit(ls_, np.arange(len(ls_)) + 0.5, 3); edges_l = np.arange(-40.25, -19.85, 0.1); la = 0.5 * (edges_l[1:] + edges_l[:-1]); pi = np.polyval(np.polyder(cf), la); assert (pi > 0).all(); pi = pi / pi.sum()
Zc = np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz'); lw = Zc['log_weight_D0'].astype(float)
hw = np.exp(lw - np.nanmax(lw)); hw = np.where(np.isfinite(hw), hw, 0); cl = Zc['latitude_deg'].astype(float)
pc, _ = np.histogram(cl, edges_l, weights=hw); pc = pc / pc.sum()
LA = np.where(pi > 0, pc / np.maximum(pi, 1e-300), 0)
def tension(LB):
    post = lambda L: (lambda p: p / p.sum())(pi * L); pA, pB, pAB = post(LA), post(LB), post(LA * LB)
    KL = lambda p: float(np.sum(np.where(p > 0, p * np.log(np.maximum(p, 1e-300) / np.maximum(pi, 1e-300)), 0)))
    def dim(p, L): lL = np.log(np.maximum(L, 1e-300)); m = (p * lL).sum(); return 2 * float((p * (lL - m) ** 2).sum())
    lnR = float(np.log((pi * LA * LB).sum()) - np.log((pi * LA).sum()) - np.log((pi * LB).sum())); lnI = KL(pA) + KL(pB) - KL(pAB); lnS = lnR - lnI
    d = dim(pA, LA) + dim(pB, LB) - dim(pAB, LA * LB)
    if d <= 0: return dict(lnR=lnR, lnS=lnS, d=d, p=np.nan, sigma=np.nan)
    x = d - 2 * lnS; p = float(stats.chi2.sf(x, d)) if x > 0 else 1.0
    return dict(lnR=lnR, lnS=lnS, d=d, p=p, sigma=float(stats.norm.isf(p / 2)) if p < 1 else 0.0)
