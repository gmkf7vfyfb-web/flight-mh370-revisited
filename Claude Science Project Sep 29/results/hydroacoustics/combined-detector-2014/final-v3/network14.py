import os
"""Network hypothesis test and seeded confirmation tests on 8 March 2014 (pre-registration v1.0, B1-B9)."""
import sys, os, pickle, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
from scipy.stats import chi2
from multiprocessing import Pool
import sigdet as SD, imosdet as ID, kadrienv as KE
from imos_calib import TailMap, COMP, CACHE, WT

T_REF = '2014-03-08T00:00:00Z'
LOGGERS = ['IMOS3250', 'IMOS3274', 'IMOS3376', 'IMOS3315', 'IMOS3275']
STATIONS = ['H01W', 'H08S'] + LOGGERS
GROUP = {'H01W': 'CL', 'H08S': 'DGS', 'IMOS3315': 'PC', 'IMOS3376': 'PC', 'IMOS3274': 'PO', 'IMOS3275': 'PO', 'IMOS3250': 'SR'}
V_MIN, V_MAX, DET = 1.465, 1.520, 0.02          # primary speed model (B5)
V_MIN_S, V_MAX_S, DET_S = 1.40, 1.56, 0.05      # sensitivity
H1 = (19 * 60 + 38, 29 * 60 + 44); H2 = (19 * 60 + 38, 55 * 60)
STEP_T = 15.0
CLS = list(SD.CLASS_ORDER)


def hms(t):
    t = t % 86400; return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:04.1f}"


# ---------------------------------------------------------------- station point series
def imos_event_day(lg, cal):
    z = np.load(f'{CACHE}/{lg.lower()}_mh370_day.npz', allow_pickle=True)
    X, n, t0 = z['x'], z['n'], z['t_start_s']
    rows = []
    for i in range(len(X)):
        if n[i] < ID.NREC * 0.95:
            continue
        x = X[i].astype(float); x -= x.mean()
        if x.std() == 0:
            continue
        g = ID.record_stats(x, WT, cal['gshape'], cal['mu'], cal['sd'], cal['tau'])
        for j, c in enumerate(ID.CENT):
            rows.append(dict(station=lg, rec=i, t_s=t0[i] + c, **{k: g[k][j] for k in COMP},
                             winner=CLS[int(g['winner'][j])], d1_clut=g['d1_clut'][j]))
    d = pd.DataFrame(rows)
    d['F'] = 0.0
    for k in COMP:
        d['p_' + k] = cal['maps'][k].p(d[k].values); d['F'] += -2 * np.nan_to_num(np.log(d['p_' + k]), nan=0.0)
    d['p_F'] = cal['maps']['F'].p(d['F'].values)
    return d


def kadri_series():
    kv = pd.read_parquet('station/station-data/kadri2024_fig9_vertices.parquet')
    out = []
    for st in ('H01W', 'H08S'):
        d = KE.traces(kv, st).dropna(subset=['E', 'pers']).reset_index(drop=True)
        d['p_E'] = KE.rank_p(d.E.values); d['p_pers'] = KE.rank_p(d.pers.values)
        d['F'] = -2 * (np.log(d.p_E) + np.log(d.p_pers)); d['p_F'] = KE.rank_p(d.F.values)
        d['rec'] = 0; d['winner'] = 'n/a'
        out.append(d)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------- window calibration
class WindowCal:
    """p of the window maximum of F over n points, per station."""
    def __init__(self, st, cal=None, series=None, rng=None):
        self.st = st
        if cal is not None:                      # IMOS: background records
            self.wmax = cal['wmax']; self.ptmap = cal['maps']['F']
        else:                                    # Kadri trace: random windows within the trace itself
            F = series.F.values; self.wmax = {}; rng = rng or np.random.default_rng(3)
            for nwin in range(1, 101):
                s = rng.integers(0, len(F) - nwin + 1, size=4000)
                self.wmax[nwin] = np.sort(np.array([F[i:i + nwin].max() for i in s]))
            Fs = np.sort(F); self.ptmap = None; self.Fs = Fs

    def p_vec(self, Fmax, nwin):
        Fmax = np.asarray(Fmax, float); nwin = np.clip(np.asarray(nwin, int), 1, max(self.wmax)); out = np.ones(len(Fmax))
        for nn in np.unique(nwin):
            m = nwin == nn; v = self.wmax[int(nn)]; L = len(v)
            pe = (L - np.searchsorted(v, Fmax[m], side='left') + 1) / (L + 1)
            if self.ptmap is not None and not os.environ.get('A6FLOOR'):
                beyond = Fmax[m] > v[-1]
                if beyond.any():
                    pe = np.where(beyond, np.minimum(pe, nn * self.ptmap.p(Fmax[m])), pe)
            out[m] = np.clip(pe, 1e-12, 1)
        return out

    def p(self, Fmax, nwin):
        nwin = int(min(max(nwin, 1), max(self.wmax)))
        v = self.wmax[nwin]; m = len(v)
        pe = (m - np.searchsorted(v, Fmax, side='left') + 1) / (m + 1)
        if self.ptmap is not None and Fmax > v[-1]:   # beyond the sample: Bonferroni on the point tail
            pe = min(pe, nwin * float(self.ptmap.p(Fmax)))
        return float(np.clip(pe, 1e-12, 1))


# ---------------------------------------------------------------- hypotheses
def hypotheses(grid_st):
    pts = grid_st[grid_st.station == 'H01W'][['point_id', 'arc_lat', 'offset_nm', 'lat', 'lon']].drop_duplicates()
    H = []
    for fam, (a, b), wid in (('H1 dive', H1, 25), ('H2 non-dive', H2, 150)):
        p = pts[pts.offset_nm.abs() <= wid]
        for t in np.arange(a, b + 1e-6, STEP_T):
            for r in p.itertuples():
                H.append((fam, r.point_id, r.arc_lat, r.offset_nm, t))
    return pd.DataFrame(H, columns=['family', 'point_id', 'arc_lat', 'offset_nm', 't_imp'])


def windows(H, G, st, vmin, vmax, det):
    g = G[G.station == st].set_index('point_id')
    d = g.loc[H.point_id, 'dist_km'].values; blocked = (g.loc[H.point_id, 'path_class'].values == 'blocked')
    a = H.t_imp.values + d / vmax; b = H.t_imp.values + d * (1 + det) / vmin
    return a, b, blocked, g.loc[H.point_id, 'path_class'].values


class Station:
    def __init__(self, st, series, wcal):
        s = series[series.station == st].sort_values('t_s')
        self.t = s.t_s.values; self.F = s.F.values; self.wcal = wcal
        self.rec = s.rec.values
        self.span = (self.t.min(), self.t.max())

    def score(self, a, b, shift=0.0, cyclic=None):
        """Window max of F and point count for windows [a,b] (data time = true time + shift)."""
        t = self.t
        if cyclic is not None:
            lo, hi = cyclic; L = hi - lo; t = lo + ((t - lo + shift) % L)
            o = np.argsort(t); t = t[o]; F = self.F[o]
        else:
            F = self.F
        i0 = np.searchsorted(t, a, 'left'); i1 = np.searchsorted(t, b, 'right'); n = i1 - i0
        cs = np.full(len(a), -np.inf)
        ok = n > 0
        # range maximum (windows are short: loop over max length)
        if ok.any():
            mx = int(n[ok].max())
            for k in range(mx):
                idx = i0 + k; m = ok & (k < n)
                cs[m] = np.maximum(cs[m], F[np.minimum(idx[m], len(F) - 1)])
        return cs, n


def network_scores(H, W, stations, shifts=None):
    """Per hypothesis: per-station p, combined chi-square p and -log10 p."""
    logp = np.zeros(len(H)); k = np.zeros(len(H), int); per = {}
    for st, S in stations.items():
        a, b, blocked, _ = W[st]
        sh = 0.0 if shifts is None else shifts[GROUP[st]]
        cyc = S.span if st in ('H01W', 'H08S') else (S.span[0], S.span[0] + 900.0 * np.ceil((S.span[1] - S.span[0]) / 900.0 + 1e-9))   # whole 15-min cycles (review 1c)
        cs, n = S.score(a, b, sh, cyclic=cyc if shifts is not None else None)
        use = (n > 0) & ~blocked
        p = np.ones(len(H))
        if use.any():
            p[use] = S.wcal.p_vec(cs[use], n[use])
        per[st] = np.where(use, p, np.nan)
        logp += np.where(use, np.log(p), 0.0); k += use
    Fn = -2 * logp
    pc = np.where(k > 0, chi2.sf(Fn, 2 * np.maximum(k, 1)), 1.0)
    return per, k, Fn, -np.log10(np.clip(pc, 1e-300, 1))
