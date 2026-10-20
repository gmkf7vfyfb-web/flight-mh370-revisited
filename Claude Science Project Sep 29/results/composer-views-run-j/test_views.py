"""Composer brief section 0.8, tests 8 and 9, as synthetic-fixture checks against closed forms (numpy).
Test 8 (arc-wide proposal): (a) defensive mixture q = (1-alpha) p_core + alpha u with exact weights u/q recovers the uniform
prior along the arc; (b) a factor composed onto the mixed proposal gives the same posterior as a direct sample from the target;
(c) the row-estimated reweighting used on run J now (r_row = u_row / q_row from the proposal's own row masses) recovers the
uniform row masses exactly and the composed posterior within Monte Carlo error.
Test 9 (views and influence): Gaussian core prior and two Gaussian factors that disagree by a known amount; views (a)-(c),
ln evidence ratio, 90 % HPD overlap, Bhattacharyya coefficient and KL influence against the closed forms.
Usage: python test_views.py [OUT.json]"""
import sys, json, numpy as np
from scipy.stats import norm
import views_common as V, views_lib as VL
rng = np.random.default_rng(20261017)
A, B = -43.0, -19.0; WID = B - A
res = {}; ok_all = True
def chk(name, got, want, tol):
    global ok_all
    ok = bool(abs(got - want) <= tol); ok_all &= ok
    res[name] = {'got': float(got), 'want': float(want), 'tol': float(tol), 'pass': ok}

def tn_pdf(x, mu, sd):
    return norm.pdf(x, mu, sd) / (norm.cdf(B, mu, sd) - norm.cdf(A, mu, sd))
def tn_rvs(n, mu, sd):
    u = rng.uniform(norm.cdf(A, mu, sd), norm.cdf(B, mu, sd), n); return norm.ppf(u, mu, sd)
def pcore_pdf(x):
    return 0.85 * tn_pdf(x, -37.5, 0.8) + 0.15 * tn_pdf(x, -30.0, 4.0)
def pcore_rvs(n):
    k = rng.random(n) < 0.85; x = np.empty(n); x[k] = tn_rvs(k.sum(), -37.5, 0.8); x[~k] = tn_rvs((~k).sum(), -30.0, 4.0); return x

N = 3_000_000; bands = np.arange(A, B + 1e-9, 1.0); uband = np.diff(bands) / WID
# ---- 8a: defensive mixture with exact weights
alpha = 0.2; isu = rng.random(N) < alpha; x = np.where(isu, rng.uniform(A, B, N), pcore_rvs(N))
q = (1 - alpha) * pcore_pdf(x) + alpha / WID; w = (1 / WID) / q
hb = np.histogram(x, bands, weights=w)[0] / w.sum(); hb2 = np.histogram(x, bands, weights=w * w)[0] / w.sum() ** 2
se = np.sqrt(np.maximum(hb2 - hb ** 2 / N, 1e-30)); z = np.max(np.abs(hb - uband) / se)
chk('8a max |z| of 1-deg band mass vs uniform (exact weights u/q)', z, 0.0, 4.5)
# ---- 8b: factor on the mixed proposal vs a direct sample from the target
L = lambda s: norm.pdf(s, -30.0, 2.0)
wf = w * L(x); m_mix = np.sum(wf * x) / wf.sum(); ess = wf.sum() ** 2 / np.sum(wf ** 2)
xd = rng.uniform(A, B, N); wd = L(xd); m_dir = np.sum(wd * xd) / wd.sum()
sd_post = np.sqrt(np.sum(wf * (x - m_mix) ** 2) / wf.sum())
chk('8b posterior mean, mixed proposal minus direct target sample (deg)', m_mix - m_dir, 0.0, 4 * sd_post * np.sqrt(1 / ess + 1 / (wd.sum() ** 2 / np.sum(wd ** 2))))
chk('8b posterior mean, mixed proposal vs closed form (deg)', m_mix, -30.0, 4 * sd_post / np.sqrt(ess))
# ---- 8c: row-estimated reweighting of the core proposal alone (the method applied to run J now)
xc = pcore_rvs(N); sub = V.sub_index(xc); rows = V.SUB_ROW
inspan = (V.ROW_MID >= A) & (V.ROW_MID < B)
S1 = np.bincount(sub, minlength=V.NSUB + 1)[:V.NSUB].astype(float)
qrow = np.bincount(rows, S1, V.NY); lrow = np.diff(V.ROW_EDGES)  # here arc length per row = latitude extent (fixture arc is a meridian)
lrow = np.where(inspan, lrow, 0.0)
r, lost = VL.arc_uniform_factors(qrow / qrow.sum(), lrow, inspan)
wr = r[rows[np.minimum(sub, V.NSUB - 1)]] * (sub < V.NSUB)
rowmass = np.bincount(rows[np.minimum(sub, V.NSUB - 1)], wr, V.NY); rowmass /= rowmass.sum()
chk('8c max |row mass - uniform row mass| (by construction)', np.max(np.abs(rowmass - lrow / lrow.sum())), 0.0, 1e-12)
wl = wr * L(xc); m_row = np.sum(wl * xc) / wl.sum(); ess_r = wl.sum() ** 2 / np.sum(wl ** 2)
# within-row (0.31 deg) the proposal shape is kept, so allow a discretisation term of row width^2/12 * d ln p/ds (bounded 0.02 deg)
chk('8c posterior mean, row-reweighted core proposal vs closed form (deg)', m_row, -30.0, 4 * sd_post / np.sqrt(ess_r) + 0.02)
res['8c effective sample of the row-reweighted factor posterior'] = float(ess_r)
# ---- 8d: a factor that abstains (not computed) north of 25 S, under the arc-uniform base: not-computed rows carried at the
# mean of the computed rows under THAT base (uniform), against the closed form
Lab = lambda s: norm.pdf(s, -30.0, 2.0); nc = xc > -25.0
S1c = np.bincount(sub, minlength=V.NSUB + 1)[:V.NSUB].astype(float)
Aa = np.bincount(sub, np.where(nc, 0.0, Lab(xc)), V.NSUB + 1)[:V.NSUB]; Nn = np.bincount(sub, nc.astype(float), V.NSUB + 1)[:V.NSUB]
Su, bars = VL.uniform_carry(r[V.SUB_ROW], S1c, [(Aa, Nn), (Aa, Nn)])
lo_, hi_ = A, -25.0; bar_cf = (norm.cdf(hi_, -30, 2) - norm.cdf(lo_, -30, 2)) / (hi_ - lo_)      # uniform-base mean of L on computed span
chk('8d uniform-base carry value vs closed form (relative)', bars[0] / bar_cf - 1.0, 0.0, 0.01)
mass_nc = np.sum((Su * r[V.SUB_ROW])[V.SUB_EDGES[:-1] >= -25.0]) / np.sum(Su * r[V.SUB_ROW])
want = bar_cf * (B - hi_) / (bar_cf * (B - hi_) + (norm.cdf(hi_, -30, 2) - norm.cdf(lo_, -30, 2)))
chk('8d mass on the abstaining span vs closed form', mass_nc, want, 0.01)

# ---- 9: two disagreeing factors on a Gaussian core prior
mu0, s0 = -37.0, 1.0; m1, s1 = -36.0, 1.5; m2, s2 = -31.0, 2.0
def prod(*g):
    prec = sum(1 / s ** 2 for _, s in g); mu = sum(m / s ** 2 for m, s in g) / prec; return mu, np.sqrt(1 / prec)
mc1, sc1 = prod((mu0, s0), (m1, s1)); mc2, sc2 = prod((mu0, s0), (m2, s2)); ma, sa = prod((mu0, s0), (m1, s1), (m2, s2))
# proposal: defensive mixture so every view is estimable from one sample (weights carry p/q)
N9 = 4_000_000; isu = rng.random(N9) < 0.5; x = np.where(isu, rng.uniform(A, B, N9), rng.normal(mu0, 3.0, N9))
q = 0.5 / WID * ((x >= A) & (x <= B)) + 0.5 * norm.pdf(x, mu0, 3.0)
wc = norm.pdf(x, mu0, s0) / q; wu = ((x >= A) & (x <= B)) / WID / q
L1, L2 = norm.pdf(x, m1, s1), norm.pdf(x, m2, s2)
edges = V.L01_EDGES; mids = V.L01_MID
H = lambda ww: np.histogram(x, edges, weights=ww)[0]
views = {'core': wc, 'a1': wu * L1, 'a2': wu * L2, 'b1': wc * L1, 'b2': wc * L2, 'all': wc * L1 * L2}
med = {k: VL.quantiles(H(v), edges, (0.5,))[0] for k, v in views.items()}
chk('9 median view (a) factor 1', med['a1'], m1, 0.01); chk('9 median view (a) factor 2', med['a2'], m2, 0.01)
chk('9 median view (b) core+1', med['b1'], mc1, 0.01); chk('9 median view (b) core+2', med['b2'], mc2, 0.01)
chk('9 median all', med['all'], ma, 0.01)
chk('9 median view (c) all-but-1 (= core+2)', med['b2'], mc2, 0.01)
# ln evidence ratio (a) vs core: ln E_core[L] - ln E_U[L]
for i, (mm, ss, LL) in enumerate(((m1, s1, L1), (m2, s2, L2)), 1):
    got = np.log(np.sum(wc * LL) / np.sum(wc)) - np.log(np.sum(wu * LL) / np.sum(wu))
    want = norm.logpdf(mm, mu0, np.hypot(s0, ss)) - np.log((norm.cdf(B, mm, ss) - norm.cdf(A, mm, ss)) / WID)
    chk(f'9 ln evidence ratio, factor {i} on core against the arc-uniform reference', got, want, 0.01)
# (c) vs all: ln E_(c)[L_E] = ln Z_all - ln Z_(c)
got = np.log(np.sum(wc * L1 * L2) / np.sum(wc * L2)); want = norm.logpdf(m1, mc2, np.hypot(sc2, s1))
chk('9 ln evidence of factor 1 given all others (c vs all)', got, want, 0.01)
# HPD overlap and Bhattacharyya (core vs view (a) for factor 2)
pa, pb = H(views['core']), H(views['a2']); ov = VL.overlap(pa, pb, 0.9)
z90 = norm.ppf(0.95); ia = (mu0 - z90 * s0, mu0 + z90 * s0); ib = (m2 - z90 * s2, m2 + z90 * s2)
want_ab = norm.cdf(ib[1], mu0, s0) - norm.cdf(ib[0], mu0, s0); want_ba = norm.cdf(ia[1], m2, s2) - norm.cdf(ia[0], m2, s2)
chk('9 share of core mass inside the factor-2 90 % HPD', ov['mass_a_in_b'], want_ab, 0.01)
chk('9 share of factor-2 (a) mass inside the core 90 % HPD', ov['mass_b_in_a'], want_ba, 0.01)
bc_want = np.sqrt(2 * s0 * s2 / (s0 ** 2 + s2 ** 2)) * np.exp(-(mu0 - m2) ** 2 / (4 * (s0 ** 2 + s2 ** 2)))
chk('9 Bhattacharyya coefficient core vs factor-2 (a)', VL.bhattacharyya(pa, pb), bc_want, 0.01)
# KL influence
klg = lambda ma_, sa_, mb_, sb_: np.log(sb_ / sa_) + (sa_ ** 2 + (ma_ - mb_) ** 2) / (2 * sb_ ** 2) - 0.5
for nm, wp, wb, lam_p, lam_b, want in (('KL(core+1 || core)', wc * L1, wc, L1, 1.0, klg(mc1, sc1, mu0, s0)),
                                       ('KL(all || all-but-2)', wc * L1 * L2, wc * L1, L1 * L2, L1, klg(ma, sa, mc1, sc1)),
                                       ('KL(all || all-but-1)', wc * L1 * L2, wc * L2, L1 * L2, L2, klg(ma, sa, mc2, sc2))):
    got = VL.kl_from_sums(np.sum(wp * np.log(lam_p / lam_b)), wp.sum(), wb.sum()); chk('9 ' + nm, got, want, 0.01)
res['ALL_PASS'] = ok_all
print(json.dumps(res, indent=1))
if len(sys.argv) > 1:
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
