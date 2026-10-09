"""Reproduction of Davey et al. (2016), Bayesian Methods in the Search for MH370, ch. 11 sect. 11.2:
the single-flaperon drift update from Global Drifter Program (GDP) undrogued trajectories.

PROVISIONAL. Reproduction target, declared ocean-model alternative `gdp-empirical` (ruling A1).
Not the module's estimator. Page numbers below are PRINTED pages (running headers).

As printed
  eq. 11.4 (p. 103)  p(x|Z, y) ~ sum_p w_p p(y|x_p) delta(x - x_p): re-weight each particle.
  p. 106             undrogued GDP trajectories through the region in February-April, 30 years;
                     "pairs of trajectories that passed close together (possibly in different years)
                     were joined", head of one with the tail of the other; "joining four trajectory
                     segments"; "each previous trajectory creates around 30 new trajectories".
  eq. 11.7 (p. 106)  x = drifter location on 8 March 2014, y = location on 29 July 2015 (508 days).
  eq. 11.8 (p. 106)  l(x) = integral over a small region R surrounding Reunion of p(y|x).
  eq. 11.9 (p. 106)  l(x) ~ [ (1/P) sum K(x - x_p) + eps ] / [ (1/P~) sum K(x - x~_p) + eps ],
                     {x_p}: trajectories passing through R "in the right time window", including the
                     joined ones; {x~_p}: all drifter locations February-April.
  p. 107             eps = 1e-4; fixed kernel, standard deviation 1 deg in latitude and longitude;
                     Fig. 11.2 title: "going to Reunion Is in 508+/-30 days".
  p. 109             updated posterior "shifted very slightly to the North, but the effect is negligible".

NOT printed, so chosen here (every one a provisional assumption, all config parameters):
  A-join-d     join distance: partner fix within JOIN_KM = 150 km of the head's end point.
  A-join-doy   partner fix within +/- JOIN_DOY = 30 days of the same day of year (any year).
               (150 km, 30 d) is CALIBRATED, not printed: on 1,500 random undrogued fixes in
               50-125 E, 45-10 S it gives a median of 28 qualifying partner drifters (10-90%:
               15-39), matching the printed "around 30 new trajectories" per join. Tight
               alternative (50 km, 15 d) gives a median of about 4 and is run as a sensitivity.
  A-join-when  a head is followed for at most SEG_MAX = 135 days (ceil(538/4)) or until its
               undrogued record ends (death, gap, or leaving the data box), then joined; at most
               4 segments (3 joins) in a synthetic trajectory, as printed.
  A-join-pick  the ~30 printed new trajectories per join are represented by Monte Carlo: each
               start launches N_MC synthetic trajectories and each join picks one partner DRIFTER
               uniformly among those qualifying (then that drifter's nearest qualifying fix). This
               preserves probability per start; Davey's literal branching multiplies paths through
               dense regions, which this choice deliberately does not reproduce.
               N_MC = 10 per start (reduced from 20 when JOIN_KM/JOIN_DOY were calibrated to
               150 km / +-30 d; disclosed 9 Oct). Seed-to-seed spread of the result is reported
               in results/davey-ch11-reproduction.md, which is how this precision is judged.
  A-join-self  when a head is cut at SEG_MAX while its own record continues, continuing on its own
               drifter is one more option in that uniform pick, so a forced cut never kills a path.
  A-R          R = disc of radius R_KM = 200 km about Reunion (21.115 S, 55.536 E).
  A-window     arrival = any daily fix inside R at elapsed time 478..538 days.
  A-domain     starts {x_p} and {x~_p}: undrogued daily fixes in Feb-Apr inside 75-125 E, 45 S-10 N
               (the Fig. 11.2 panel extent); the same start set feeds numerator and denominator.
  A-kde        Gaussian kernel isotropic in degrees (no cos-latitude), densities per deg^2,
               evaluated by binning at 0.05 deg and Gaussian filtering (zero outside the box).
  A-nojoin-end a synthetic trajectory with no qualifying partner simply ends (non-arrival). This
               inherits the survivor bias the brief warns about; it is Davey's construction.
"""
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

REUNION = (-21.115, 55.536)
EARTH_KM = 6371.0
CONFIG = dict(JOIN_KM=150.0, JOIN_DOY=30, SEG_MAX=135, N_SEG=4, N_MC=10, R_KM=200.0,
              T_LO=478, T_HI=538, BOX=(75.0, 125.0, -45.0, 10.0), MONTHS=(2, 3, 4),
              SIGMA_DEG=1.0, EPS=1e-4, BIN_DEG=0.05, SEED=20140308)


def unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def gc_km(lat1, lon1, lat2, lon2):
    la1, la2 = np.radians(lat1), np.radians(lat2)
    dlo = np.radians(lon2 - lon1)
    c = np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(dlo)
    return EARTH_KM * np.arccos(np.clip(c, -1.0, 1.0))


def month_of(day):
    return (day.astype("datetime64[D]").astype("datetime64[M]").astype(int) % 12) + 1


def doy_of(day):
    d = day.astype("datetime64[D]")
    return (d - d.astype("datetime64[Y]")).astype(int)


class Tracks:
    """Daily undrogued fixes sorted by (drifter, day), cut into contiguous runs."""

    def __init__(self, drifter, day, lat, lon, r_km=CONFIG["R_KM"]):
        self.drifter, self.day = np.asarray(drifter), np.asarray(day)
        self.lat, self.lon = np.asarray(lat, float), np.asarray(lon, float)
        n = len(day)
        brk = np.ones(n, bool)
        brk[1:] = (self.drifter[1:] != self.drifter[:-1]) | (self.day[1:] - self.day[:-1] != 1)
        run_id = np.cumsum(brk) - 1
        starts = np.flatnonzero(brk)
        ends = np.r_[starts[1:], n] - 1
        self.run_end = ends[run_id]           # last index of the contiguous run holding each fix
        self.doy = doy_of(self.day)
        self.month = month_of(self.day)
        self.inR = gc_km(self.lat, self.lon, *REUNION) <= r_km
        self.cR = np.r_[0, np.cumsum(self.inR)]
        self.tree = None

    def any_inR(self, a, b):
        """vectorised: any inR fix in index range [a, b] (inclusive); empty if b < a."""
        a, b = np.asarray(a), np.asarray(b)
        ok = b >= a
        out = np.zeros(a.shape, bool)
        out[ok] = (self.cR[b[ok] + 1] - self.cR[a[ok]]) > 0
        return out

    def build_tree(self):
        self.tree = cKDTree(unit(self.lat, self.lon))


def partners(tr, idx, join_km, join_doy, cache):
    """For join point fix idx: one candidate fix per qualifying other drifter (nearest fix)."""
    if idx in cache:
        return cache[idx]
    chord = 2.0 * np.sin(join_km / EARTH_KM / 2.0)
    cand = np.asarray(tr.tree.query_ball_point(unit(tr.lat[idx:idx + 1], tr.lon[idx:idx + 1])[0], chord),
                      dtype=np.int64)
    if len(cand):
        dd = np.abs(tr.doy[cand] - tr.doy[idx])
        dd = np.minimum(dd, 365 - dd)
        ok = (dd <= join_doy) & (tr.drifter[cand] != tr.drifter[idx]) & (tr.run_end[cand] > cand)
        cand, dd = cand[ok], dd[ok]
    if len(cand):
        dist = gc_km(tr.lat[idx], tr.lon[idx], tr.lat[cand], tr.lon[cand])
        # per drifter: nearest fix, ties broken by closest day of year, then earliest index
        o = np.lexsort((cand, dd, np.round(dist, 6), tr.drifter[cand]))
        cand = cand[o]
        first = np.r_[True, tr.drifter[cand][1:] != tr.drifter[cand][:-1]]
        cand = cand[first]
    cache[idx] = cand
    return cand


def simulate(tr, start_idx, cfg=CONFIG, rng=None, n_mc=None, n_seg=None, stats=None):
    """Return arrival fraction per start (shape len(start_idx)).

    Each start launches n_mc synthetic trajectories built from at most n_seg real segments
    (n_seg - 1 joins; continuing on the same drifter is not a join). n_seg = 1 is the UN-JOINED
    version: real drifters only, each followed to the end of its undrogued record or 538 days.
    """
    rng = rng or np.random.default_rng(cfg["SEED"])
    n_mc = cfg["N_MC"] if n_mc is None else n_mc
    n_seg = cfg["N_SEG"] if n_seg is None else n_seg
    if n_seg > 1 and tr.tree is None:
        tr.build_tree()
    owner = np.repeat(np.arange(len(start_idx)), n_mc)
    cur = np.repeat(np.asarray(start_idx), n_mc)
    elapsed = np.zeros(len(cur), np.int64)
    joins_left = np.full(len(cur), n_seg - 1, np.int64)
    arrived = np.zeros(len(cur), bool)
    alive = np.ones(len(cur), bool)
    cache = {}
    ncand = []
    n_joins_made = 0
    for _ in range(cfg["T_HI"] // max(cfg["SEG_MAX"], 1) + n_seg + 2):
        k = np.flatnonzero(alive)
        if len(k) == 0:
            break
        i = cur[k]
        seg_len = np.where(joins_left[k] > 0, cfg["SEG_MAX"], cfg["T_HI"])
        end = np.minimum(i + seg_len, tr.run_end[i])
        lo = np.maximum(i, i + cfg["T_LO"] - elapsed[k])
        hi = np.minimum(end, i + cfg["T_HI"] - elapsed[k])
        hit = tr.any_inR(lo, hi)
        arrived[k[hit]] = True
        elapsed[k] += end - i
        own_more = tr.run_end[end] > end
        done = hit | (elapsed[k] >= cfg["T_HI"]) | ((joins_left[k] == 0) & ~own_more)
        alive[k[done]] = False
        k2, ends = k[~done], end[~done]
        newcur = np.full(len(k2), -1, np.int64)
        can_join = joins_left[k2] > 0
        for u in np.unique(ends[can_join]):
            c = partners(tr, int(u), cfg["JOIN_KM"], cfg["JOIN_DOY"], cache)
            sel = np.flatnonzero((ends == u) & can_join)
            ncand.append(len(c))
            if tr.run_end[u] > u:          # cut at SEG_MAX with its own record continuing:
                c = np.r_[c, u]            # continuing on itself is one of the options (A-join-self)
            if len(c):
                newcur[sel] = c[rng.integers(0, len(c), len(sel))]
        newcur[~can_join] = ends[~can_join]          # no joins left: continue on own record
        joined = can_join & (newcur >= 0) & (newcur != ends)
        joins_left[k2[joined]] -= 1
        n_joins_made += int(joined.sum())
        dead = newcur < 0
        alive[k2[dead]] = False
        cur[k2[~dead]] = newcur[~dead]
    assert not alive.any(), "simulate: paths still alive after the iteration bound"
    if stats is not None:
        stats["n_joins_made"] = n_joins_made
        stats["mean_joins_per_path"] = n_joins_made / len(cur)
        stats["n_partner_lists"] = len(ncand)
        stats["partners_median"] = float(np.median(ncand)) if ncand else float("nan")
        stats["partners_q10_q90"] = [float(np.percentile(ncand, 10)), float(np.percentile(ncand, 90))] if ncand else []
        stats["frac_no_partner"] = float(np.mean(np.asarray(ncand) == 0)) if ncand else float("nan")
    return np.bincount(owner, weights=arrived, minlength=len(start_idx)) / n_mc


def kde_grid(lat, lon, weights, box, sigma_deg, bin_deg):
    """Normalised Gaussian KDE (per deg^2) on a regular grid by binning + Gaussian filtering."""
    lo0, lo1, la0, la1 = box
    nx, ny = int(round((lo1 - lo0) / bin_deg)), int(round((la1 - la0) / bin_deg))
    H, _, _ = np.histogram2d(lat, lon, bins=[ny, nx], range=[[la0, la1], [lo0, lo1]], weights=weights)
    tot = np.sum(weights)
    D = ndimage.gaussian_filter(H / (tot * bin_deg * bin_deg), sigma_deg / bin_deg, mode="constant",
                                truncate=5.0)
    return D


def sample_grid(D, box, bin_deg, lat, lon):
    """Bilinear interpolation of a grid (cell centres) at points; 0 outside the box."""
    lo0, lo1, la0, la1 = box
    r = (np.asarray(lat) - la0) / bin_deg - 0.5
    c = (np.asarray(lon) - lo0) / bin_deg - 0.5
    return ndimage.map_coordinates(D, [r, c], order=1, mode="constant", cval=0.0)


def likelihood(start_lat, start_lon, arrive_w, eval_lat, eval_lon, cfg=CONFIG, sigma=None, eps=None):
    """Eq. 11.9: [KDE(arrivers) + eps] / [KDE(all Feb-Apr starts) + eps] at the evaluation points.

    arrive_w: per-start arrival weight (fraction of that start's synthetic trajectories that
    reached R in the window). The numerator is normalised by its own total weight (the printed 1/P).
    Returns (l, num, den).
    """
    sigma = cfg["SIGMA_DEG"] if sigma is None else sigma
    eps = cfg["EPS"] if eps is None else eps
    box, b = cfg["BOX"], cfg["BIN_DEG"]
    Dn = kde_grid(start_lat, start_lon, arrive_w, box, sigma, b)
    Dd = kde_grid(start_lat, start_lon, np.ones(len(start_lat)), box, sigma, b)
    num = sample_grid(Dn, box, b, eval_lat, eval_lon)
    den = sample_grid(Dd, box, b, eval_lat, eval_lon)
    return (num + eps) / (den + eps), num, den


def kde_exact(px, py, w, x, y, sigma):
    """Direct Gaussian KDE (per deg^2), for fixtures and spot checks."""
    w = np.asarray(w, float)
    d2 = (np.asarray(x)[:, None] - px[None, :]) ** 2 + (np.asarray(y)[:, None] - py[None, :]) ** 2
    return (np.exp(-d2 / (2 * sigma ** 2)) @ w) / (w.sum() * 2 * np.pi * sigma ** 2)


def weighted_quantiles(edges_lat, mass, qs):
    """Quantiles of a latitude histogram (mass per bin, bins [edges[i], edges[i+1]]), linear within bins."""
    cdf = np.r_[0.0, np.cumsum(mass)] / np.sum(mass)
    return np.interp(qs, cdf, edges_lat)


def ess_fraction(w, l):
    """Kish effective-sample fraction of a reweighting: (sum w l)^2 / (sum w * sum w l^2)."""
    w = np.asarray(w, float) / np.sum(w)
    return float(np.sum(w * l) ** 2 / np.sum(w * l * l))
