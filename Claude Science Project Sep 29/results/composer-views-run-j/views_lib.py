"""Statistics used by the composer views (run J) and by its synthetic tests 8 and 9. Pure numpy.
All functions take unnormalised masses on a common grid (1-D latitude bins or 2-D equal-area cells)."""
import numpy as np


def hpd_mask(mass, level):
    """Highest-posterior-density region on an EQUAL-AREA grid (density proportional to mass): smallest set of cells holding `level`."""
    p = np.asarray(mass, float).ravel(); tot = p.sum()
    o = np.argsort(-p, kind='stable'); c = np.cumsum(p[o]) / tot
    sel = np.zeros(p.size, bool); sel[o[:min(np.searchsorted(c, level) + 1, p.size)]] = True
    return sel.reshape(np.shape(mass))


def hpd_mask_density(mass, area, level):
    """HPD on an unequal-area grid: rank by density mass/area."""
    p = np.asarray(mass, float); d = np.where(area > 0, p / np.where(area > 0, area, 1), 0)
    o = np.argsort(-d, kind='stable'); c = np.cumsum(p[o]) / p.sum()
    sel = np.zeros(p.size, bool); sel[o[:min(np.searchsorted(c, level) + 1, p.size)]] = True
    return sel


def overlap(pa, pb, level=0.9):
    """Share of A's mass inside B's HPD region and of B's mass inside A's; area share of each region inside the other."""
    pa = np.asarray(pa, float).ravel() / np.sum(pa); pb = np.asarray(pb, float).ravel() / np.sum(pb)
    ra, rb = hpd_mask(pa, level).ravel(), hpd_mask(pb, level).ravel()
    return {'mass_a_in_b': float(pa[rb].sum()), 'mass_b_in_a': float(pb[ra].sum()),
            'area_a_in_b': float((ra & rb).sum() / ra.sum()), 'area_b_in_a': float((ra & rb).sum() / rb.sum())}


def bhattacharyya(pa, pb):
    pa = np.asarray(pa, float).ravel() / np.sum(pa); pb = np.asarray(pb, float).ravel() / np.sum(pb)
    return float(np.sum(np.sqrt(pa * pb)))


def quantiles(hist, edges, qs=(0.05, 0.5, 0.95)):
    """Quantiles of a 1-D histogram with linear interpolation inside bins."""
    h = np.asarray(hist, float); c = np.concatenate([[0], np.cumsum(h)]) / h.sum()
    return [float(np.interp(q, c, edges)) for q in qs]


def kl_from_sums(sum_w_dlnL, Zp, Zb):
    """KL(posterior P || base B) in nats when P = B x Lambda: E_P[ln Lambda] - ln(Z_P / Z_B).
    sum_w_dlnL = sum of w_P ln(Lambda_P/Lambda_B) on the pooled sample, Zp = sum w_P, Zb = sum w_B (same pooled sample)."""
    return float(sum_w_dlnL / Zp - np.log(Zp / Zb))


def modes_1d(hist, mids, smooth_bins=15, min_mass=0.001):
    """Modes of a 1-D latitude PDF: Gaussian-smoothed (sd = smooth_bins bins); basins split at the local minima; every basin with
    mass >= min_mass reported with its peak position and mass (mass from the unsmoothed histogram)."""
    h = np.asarray(hist, float) / np.sum(hist)
    k = np.arange(-4 * smooth_bins, 4 * smooth_bins + 1); ker = np.exp(-0.5 * (k / smooth_bins) ** 2); ker /= ker.sum()
    s = np.convolve(h, ker, mode='same')
    d = np.diff(s); peaks = [i for i in range(1, len(s) - 1) if d[i - 1] > 0 and d[i] <= 0 and s[i] > 0]
    mins = [i for i in range(1, len(s) - 1) if d[i - 1] < 0 and d[i] >= 0]
    bounds = [0] + mins + [len(s)]
    out = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        pk = [p for p in peaks if a <= p < b]
        if not pk:
            continue
        p = max(pk, key=lambda i: s[i]); m = float(h[a:b].sum())
        out.append({'peak_lat': float(mids[p]), 'mass': m, 'from_lat': float(mids[a]), 'to_lat': float(mids[min(b, len(mids)) - 1])})
    # merge basins below min_mass into the neighbour with the higher peak
    while len(out) > 1 and min(o['mass'] for o in out) < min_mass:
        i = int(np.argmin([o['mass'] for o in out])); j = i - 1 if i == len(out) - 1 or (i > 0 and out[i - 1]['mass'] > out[i + 1]['mass']) else i + 1
        a, b = sorted((i, j)); keep = out[a] if out[a]['mass'] >= out[b]['mass'] else out[b]
        merged = dict(keep, mass=out[a]['mass'] + out[b]['mass'], from_lat=out[a]['from_lat'], to_lat=out[b]['to_lat'])
        out[a:b + 1] = [merged]
    return out


def arc_uniform_factors(q_row, arc_len_row, span_mask):
    """Row reweighting r = u / q that makes the proposal's row masses uniform per unit arc length over the span.
    Rows in the span with no proposal mass cannot be reached: their target share is returned as `lost`."""
    u = np.where(span_mask, arc_len_row, 0.0); u = u / u.sum()
    reach = span_mask & (q_row > 1e-280)          # a row whose proposal mass underflows cannot be reweighted
    r = np.where(reach, u / np.where(reach, q_row, 1.0), 0.0)
    return r, float(u[span_mask & ~reach].sum())


def gc_nm(lat1, lon1, lat2, lon2):
    la1, lo1, la2, lo2 = map(np.radians, (lat1, lon1, lat2, lon2))
    return 3440.065 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))


def uniform_carry(r_sub, S1core, parts):
    """Single-factor likelihood (ocean models averaged) under a base with sub-bin weights r: not-computed rows carried at the
    mean of the computed rows UNDER THAT BASE (ruling 15 Oct, applied per product base). parts = [(A_sub, N_sub), per model]."""
    S = 0.0; bars = []
    for A_, N_ in parts:
        den = np.sum(r_sub * (S1core - N_)); bar = np.sum(r_sub * A_) / den if den > 0 else 0.0; bars.append(bar)
        S = S + 0.5 * (A_ + N_ * bar)
    return S, bars
