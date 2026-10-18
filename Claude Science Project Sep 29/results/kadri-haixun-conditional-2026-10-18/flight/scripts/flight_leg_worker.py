"""Kadri / Haixun conditional, FLIGHT leg (pre-registration Q1-Q3), per-seed worker. Run J end of flight, compact impacts.

Weights per impact row are end of flight's own cells, built by option_table_0019.seed_terms UNCHANGED (source exec'd with only
the final reduction replaced by `return cells, f4, g`, as results/drift-runj-2026-10-17/compose_drift_runj.py). Pooled row mass
is P_s / K_s x exp(cell), P_s = core P(family) of the stratum, K_s = seeds in the stratum (option_table_0019.main).
Acoustic per-row likelihood (pre-registration Q2, unchanged):
  t_pred = t_impact + d / c, c = 1.48 km/s, d = WGS84 geodesic impact -> H01W (km); b = WGS84 azimuth H01W -> impact.
  L = N(t_obs - t_pred; 0, s_t) N(b_obs - b; 0, s_b), s_t^2 = (d 0.015 / 1.48^2)^2 + 5^2 s^2, s_b = 0.5 or 1.0 deg.
Locality L: bearing strip R7 - 60 km <= d <= R7 + 250 km, |cross-track| <= d tan(1 deg); discs 50/100/200/400 km around the
sea-level arc crossing X (R7 = 1,591.3 km on 306.18 deg) and around Haixun 01 (25.975 S 101.461 E).
"""
import sys, json, pathlib, inspect, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scorer'))
import displacement_hist as DH
DH.SATCOM_CSV = (HERE.parent / 'scorer' / 'satcom-observations.csv').resolve()
import option_table_0019 as OT
OT.SATCOM_CSV = DH.SATCOM_CSV
from pyproj import Geod
from scipy.special import logsumexp

src = inspect.getsource(OT.seed_terms)
src = src[:src.index('    out = {}')] + '    return cells, f4, g\n'
_ns = dict(OT.__dict__); exec(src, _ns); seed_cells = _ns['seed_terms']

GEOD = Geod(ellps='WGS84')
H01 = (-34.8903, 114.1426); AZ = 306.18; R7 = 1591.3; C_KMS = 1.48
_lo, _la, _ = GEOD.fwd(H01[1], H01[0], AZ, R7 * 1e3); XC = (float(_la), float(_lo))
HX = (-25.975, 101.461)
T_REF = 1394236800.0                       # 2014-03-08 00:00:00 UTC
T_OBS = {'T': T_REF + 52 * 60 + 3, 'C': T_REF + 54 * 60 + 30}
VARIANTS = [('T', 0.5), ('T', 1.0), ('C', 0.5), ('C', 1.0)]
VNAME = [f'{b}{sb:.1f}' for b, sb in VARIANTS]
DS = [f'D{d}' for d in range(6)]
KEYS = [f'{d} total q=0.333 (C2 silent)' for d in DS] + [f'{d}xC1' for d in DS] + [f'{d}xC2 silent' for d in DS]
HEAD = KEYS[:6]
REGIONS = ['all', 'strip'] + [f'X{r}' for r in (50, 100, 200, 400)] + [f'H{r}' for r in (50, 100, 200, 400)]
HREG = ['all', 'strip', 'X100', 'X200', 'H100', 'H200']
# map grids
LOC = dict(lat0=-34.0, lat1=-18.0, lon0=92.0, lon1=110.0, step=0.05)
WIDE = dict(lat0=-46.0, lat1=-16.0, lon0=76.0, lon1=114.0, step=0.1)
def grid_shape(G): return int(round((G['lat1'] - G['lat0']) / G['step'])), int(round((G['lon1'] - G['lon0']) / G['step']))
def grid_index(G, lat, lon):
    ni, nj = grid_shape(G); i = np.floor((lat - G['lat0']) / G['step']).astype(np.int64); j = np.floor((lon - G['lon0']) / G['step']).astype(np.int64)
    ok = (i >= 0) & (i < ni) & (j >= 0) & (j < nj) & np.isfinite(lat) & np.isfinite(lon)
    return np.where(ok, i * nj + j, ni * nj), ni * nj   # last bin = outside
TB = np.arange(0, 5400 + 1, 60.0)           # impact time after 00:00 UTC, 1-min bins to 01:30
FB = np.arange(-1800, 5400 + 1, 60.0)       # realised flame-out time after 00:00 (23:30 -> 01:30)
AB = np.arange(0, 3600 + 1, 60.0)           # minutes aloft after flame-out (0-60)
KEEP_COLS = ['parent', 'family', 'weight', 'unix_s', 'takeover_unix_s', 'latent:realised_flameout_unix_s', 'latent:onset_unix_s',
             'latitude_deg', 'longitude_deg', 'arc_distance_nm', 'velocity_east_mps', 'velocity_north_mps', 'velocity_up_mps',
             'flight_path_angle_deg', 'mass_kg', 'takeover_latitude_deg', 'takeover_longitude_deg', 'takeover_altitude_ft',
             'bto_residual_us:m0019a', 'bto_residual_us:m0019b', 'bfo_innovation_hz:m0019a', 'bfo_innovation_hz:m0019b',
             'loglik:r600/no-offset', 'loglik:both/no-offset', 'loglik:both/startup-offset',
             'latent:onset_mechanism', 'latent:control_realised', 'latent:recovery_attempted', 'latent:profile_shape',
             'latent:engines_thrusting_at_onset', 'latent:spiral_divergent', 'latent:max_descent_rate_fpm', 'latent:time_descending_s',
             'latent:timed_out', 'latent:last_burst_latitude_deg', 'latent:last_burst_longitude_deg',
             'latent:state_m0019a_altitude_ft', 'latent:state_m0019a_vertical_speed_fpm', 'latent:state_m0019b_altitude_ft',
             'latent:state_m0019b_vertical_speed_fpm', 'latent:impact_heading_deg', 'latent:impact_bank_deg',
             'latent:pushover_drawn', 'latent:pushover_rate_fpm', 'latent:pitchdown_drawn', 'latent:pitchdown_n_g',
             'latent:turns_davey_begun', 'latent:turns_terminal_begun', 'latent:sweep_begun', 'latent:circuit_begun',
             'latent:circuit_final_kind', 'latent:heading_change_deg', 'latent:pushover_to_surface', 'latent:davey_tau_h',
             'latent:turn_ln_rate_per_min', 'latent:inflight_p_breakup_to_m0019b', 'latent:breakup_p_intact', 'latent:breakup_p_fragmented',
             'latent:ap_loss_config', 'latent:free_dynamics_started_s', 'latent:residual_bank_sign', 'kinetic_energy_j', 'vertical_kinetic_energy_j']


def geometry(lat, lon):
    n = len(lat); one = np.ones(n)
    az, _, d = GEOD.inv(H01[1] * one, H01[0] * one, lon, lat); d = d / 1e3
    _, _, dx = GEOD.inv(XC[1] * one, XC[0] * one, lon, lat); _, _, dh = GEOD.inv(HX[1] * one, HX[0] * one, lon, lat)
    db = (AZ - az + 540.0) % 360.0 - 180.0                        # b_obs - b_i, wrapped
    xt = 6371.0 * np.arcsin(np.clip(np.sin(d / 6371.0) * np.sin(np.radians(db)), -1, 1))
    return d, az, db, xt, dx / 1e3, dh / 1e3


def acoustic(t_imp, d, db):
    st = np.sqrt((d * 0.015 / C_KMS ** 2) ** 2 + 25.0)
    out, z2 = {}, {}
    for (b, sb), vn in zip(VARIANTS, VNAME):
        r = T_OBS[b] - (t_imp + d / C_KMS)
        lt = -0.5 * (r / st) ** 2 - np.log(np.sqrt(2 * np.pi) * st)
        lb = -0.5 * (db / sb) ** 2 - np.log(np.sqrt(2 * np.pi) * sb)
        out[vn] = np.where(np.isfinite(lt + lb), lt + lb, -np.inf); z2[vn] = (r / st) ** 2 + (db / sb) ** 2
    return out, z2


def lse(x):
    x = x[np.isfinite(x)]
    return float(logsumexp(x)) if len(x) else -np.inf


def parent_ess_terms(par, lm):
    """ln sum_p (sum_{i in p} m_i)^2 and number of parents with positive mass, from log masses lm."""
    fin = np.isfinite(lm)
    if not fin.any(): return -np.inf, 0
    s = lm[fin].max(); M = np.bincount(par[fin], np.exp(lm[fin] - s))
    return float(np.log((M * M).sum()) + 2 * s), int((M > 0).sum())


def reduce_masses(lm, regions, par, f4):
    """lm: per-row log mass (already including ln P/K); regions: name -> row index array (None = all rows).
    Returns per region ln S1, ln S2, family ln S1/S2 (A1, A2, B), ln sum_p M_p^2 and parents with positive mass."""
    fin = np.isfinite(lm)
    if not fin.any():
        z = {'l1': -np.inf, 'l2': -np.inf, 'fam1': [-np.inf] * 3, 'fam2': [-np.inf] * 3, 'par2': -np.inf, 'npar': 0}
        return {rn: dict(z) for rn in regions}
    s = float(lm[fin].max()); e = np.where(fin, np.exp(lm - s), 0.0)
    L = lambda v, k=1: float(np.log(v) + k * s) if v > 0 else -np.inf
    out = {}
    for rn, ix in regions.items():
        ee = e if ix is None else e[ix]; ff = f4 if ix is None else f4[ix]; pp = par if ix is None else par[ix]
        fb = np.nan_to_num(ff, nan=0).astype(np.int64)
        f1 = np.bincount(fb, ee, 4); f2 = np.bincount(fb, ee * ee, 4)
        M = np.bincount(pp, ee)
        out[rn] = {'l1': L(ee.sum()), 'l2': L((ee * ee).sum(), 2), 'fam1': [L(f1[c]) for c in (1, 2, 3)], 'fam2': [L(f2[c], 2) for c in (1, 2, 3)],
                   'par2': L((M * M).sum(), 2), 'npar': int((M > 0).sum())}
    return out


def logbincount(idx, lm, n):
    """(log offset, scaled histogram) of exp(lm) binned by idx."""
    fin = np.isfinite(lm)
    if not fin.any(): return -np.inf, np.zeros(n)
    s = lm[fin].max(); return float(s), np.bincount(idx[fin], np.exp(lm[fin] - s), n)


def process(job):
    stratum, seed, P, K, eof_root, core_root, rows_dir = job
    sd = pathlib.Path(eof_root) / stratum / f'seed-{seed}'
    cells, f4, g = seed_cells(sd, pathlib.Path(core_root) / stratum / 'bto-bfo' / f'seed-{seed}' / 'handoff-m0011' / 'handoff.npy')
    c0 = float(np.log(P / K))
    lm = {k: cells[k] + c0 for k in KEYS}; del cells
    tau = np.load(sd / 'tau90_v1.npz'); att = np.load(sd / 'attitude_v1.npz')
    side = {'tau90_s': tau['tau90_s'], 'energy_transferred_j': tau['energy_transferred_j'], 'decel_g': tau['decel_g'],
            'bank_deg_att': att['bank_deg'], 'bank_source': att['bank_source'], 'n_pulses': att['n_pulses']}
    res = analyse(lm, KEYS, HEAD, f4, g, side, pathlib.Path(rows_dir) / f'{stratum}-seed-{seed}.npz')
    res.update({'stratum': stratum, 'seed': seed, 'c0': c0})
    return res


def process_joined(job):
    """Arm V2 joined at 00:11 (smoke/joined_v2.py main(), weights reproduced line for line; D0-D4, total q = 1/3, C2 silent)."""
    import joined_v2 as JV
    seed, K, jroot, core_root, rows_dir = job
    hd = pathlib.Path(core_root) / 'run-j-waypoints' / 'bto-bfo' / f'seed-{seed}'
    h2241, h0011 = hd / 'handoff-m2241' / 'handoff.toml.gz', hd / 'handoff-m0011' / 'handoff.toml.gz'
    T0, T1 = JV.stop_unix(h2241), JV.stop_unix(h0011); dlnz = JV.stop_lnz(h0011) - JV.stop_lnz(h2241)
    m1, g1, _ = JV.load(pathlib.Path(jroot) / 'J2241', seed); m2, g2, _ = JV.load(pathlib.Path(jroot) / 'J0011', seed)
    p1 = JV.Prior(m1["config"]["hypotheses"]["end-of-flight"]["onset"]); p2 = JV.Prior(m2["config"]["hypotheses"]["end-of-flight"]["onset"])
    tk1 = g1("takeover_unix_s"); fo1 = g1("latent:realised_flameout_unix_s"); mech1 = g1("latent:onset_mechanism")
    s1 = (tk1 < T1) & ((mech1 == 0) | (mech1 == 1)) & ~(np.isfinite(fo1) & (fo1 < JV.T_M0011_BURST))
    tau1 = g1("latent:onset_unix_s"); P1 = tau1 + g1("latent:predicted_endurance_at_onset_s")
    with np.errstate(invalid="ignore"):
        lr1 = np.where(s1, p2.log_density(mech1, tau1, P1, T0) - p1.log_density(mech1, tau1, P1, T0), -np.inf)
    s1 = s1 & np.isfinite(lr1)
    lw1 = np.log(g1("weight")) + np.where(s1, lr1, 0.0); c1 = JV.cells(m1, g1, "m0011+")
    tau2 = g2("latent:onset_unix_s"); P2 = tau2 + g2("latent:predicted_endurance_at_onset_s"); mech2 = g2("latent:onset_mechanism")
    with np.errstate(invalid="ignore"):
        lr = p2.log_density(mech2, tau2, P2, T0) - p2.log_density(mech2, tau2, P2, T1)
    s2 = np.isfinite(lr) & (P2 >= T1)
    lw2 = np.log(g2("weight")) + np.where(s2, lr, -np.inf); c2 = JV.cells(m2, g2, "")
    f4 = np.r_[JV.family(g1), JV.family(g2)]
    c0 = float(np.log(1.0 / K)); lm = {}
    jkeys = [f'D{d} joined V2' for d in range(5)]
    for d, kk in zip(range(5), jkeys):
        lm[kk] = np.r_[np.where(s1, lw1 + c1[f'D{d}'], -np.inf), lw2 + dlnz + c2[f'D{d}']] + c0
    del c1, c2
    n1 = len(lw1)
    def g(name):
        a = g1(name) if name in m1['impact_columns'] else np.full(n1, np.nan)
        b = g2(name) if name in m2['impact_columns'] else np.full(len(lw2), np.nan)
        return np.r_[a, b]
    side = {}
    res = analyse(lm, jkeys, jkeys, f4, g, side, pathlib.Path(rows_dir) / f'joined-v2-seed-{seed}.npz')
    res.update({'stratum': 'joined-v2', 'seed': seed, 'c0': c0, 'n_S1_rows': int(n1), 'n_S2_rows': int(len(lw2)),
                'lnZ_seed': {kk: (float(logsumexp(lm[kk][np.isfinite(lm[kk])])) - c0) for kk in jkeys}})
    return res


def analyse(lm, keys, head, f4, g, side, rows_path):
    lat, lon, t = g('latitude_deg'), g('longitude_deg'), g('unix_s'); par = g('parent').astype(np.int64)
    fo = g('latent:realised_flameout_unix_s')
    d, az, db, xt, dx, dh = geometry(lat, lon)
    masks = {'all': np.ones(len(lat), bool), 'strip': (d >= R7 - 60) & (d <= R7 + 250) & (np.abs(xt) <= d * np.tan(np.radians(1.0)))}
    for r in (50, 100, 200, 400): masks[f'X{r}'] = dx <= r
    for r in (50, 100, 200, 400): masks[f'H{r}'] = dh <= r
    lnL, z2 = acoustic(t, d, db)
    RIX = {rn: (None if rn == 'all' else np.nonzero(mk)[0]) for rn, mk in masks.items()}
    res = {'rows': int(len(lat)),
           'geom_rows': {rn: int(mk.sum()) for rn, mk in masks.items()},
           'geom_parents': {rn: int(len(np.unique(par[mk]))) for rn, mk in masks.items()},
           'prior': {}, 'acoustic': {}, 'hist': {}, 'maps': {}}
    # Q1: posterior mass in each region, per cell
    for k in keys:
        res['prior'][k] = reduce_masses(lm[k], RIX, par, f4)
    # Q2: Bayes-factor numerators sum w L, in log; families; share in regions; parent ESS
    for k in keys:
        res['acoustic'][k] = {vn: reduce_masses(lm[k] + lnL[vn], {r_: RIX[r_] for r_ in ('all', 'strip', 'X200', 'H200')}, par, f4) for vn in VNAME}
    # distributions for headline keys
    ti = np.clip(np.searchsorted(TB, t - T_REF, side='right') - 1, 0, len(TB) - 2)
    t_ok = np.isfinite(t) & (t - T_REF >= TB[0]) & (t - T_REF < TB[-1])
    ti = np.where(t_ok, ti, len(TB) - 1)
    fi = np.where(np.isfinite(fo), np.clip(np.searchsorted(FB, fo - T_REF, side='right') - 1, 0, len(FB) - 2), len(FB) - 1)
    al = t - fo
    ai = np.where(np.isfinite(al) & (al >= 0) & (al < AB[-1]), np.clip(np.searchsorted(AB, al, side='right') - 1, 0, len(AB) - 2),
                  np.where(np.isfinite(al) & (al >= AB[-1]), len(AB) - 1, len(AB)))   # last two bins: >=60 min, no flame-out before impact
    for k in head:
        hk = {}
        for rn in HREG:
            ix = RIX[rn]; x = lm[k] if ix is None else lm[k][ix]; s_ = (lambda a: a) if ix is None else (lambda a, ix=ix: a[ix])
            hk[rn] = {'t': logbincount(s_(ti), x, len(TB)), 'fo': logbincount(s_(fi), x, len(FB)), 'aloft': logbincount(s_(ai), x, len(AB) + 1)}
        for vn in VNAME:
            x = lm[k] + lnL[vn]
            hk['cond_' + vn] = {'t': logbincount(ti, x, len(TB)), 'fo': logbincount(fi, x, len(FB)), 'aloft': logbincount(ai, x, len(AB) + 1)}
        res['hist'][k] = hk
    # maps (log offset, scaled)
    iL, nL = grid_index(LOC, lat, lon); iW, nW = grid_index(WIDE, lat, lon)
    for k in head:
        res['maps'][f'{k}|prior|wide'] = logbincount(iW, lm[k], nW + 1)
        res['maps'][f'{k}|prior|loc'] = logbincount(iL, lm[k], nL + 1)
        for vn in VNAME:
            res['maps'][f'{k}|{vn}|loc'] = logbincount(iL, lm[k] + lnL[vn], nL + 1)
            res['maps'][f'{k}|{vn}|wide'] = logbincount(iW, lm[k] + lnL[vn], nW + 1)
    # stored rows: acoustically compatible (6-sigma, s_b = 1 deg) or top 500 per headline cell x branch, or inside strip/X200/H200
    keep = (z2['T1.0'] < 36) | (z2['C1.0'] < 36)
    loc_keep = masks['strip'] | masks['X200'] | masks['H200']
    for k in head:
        for vn in ('T1.0', 'C1.0', 'T0.5', 'C0.5'):
            x = lm[k] + lnL[vn]; fin = np.isfinite(x)
            if fin.sum() > 500:
                thr = np.partition(x[fin], -500)[-500]; keep |= fin & (x >= thr)
            else: keep |= fin
    sel = keep | loc_keep
    # drop rows with zero mass in every cell
    anyfin = np.zeros(len(lat), bool)
    for k in keys: anyfin |= np.isfinite(lm[k])
    sel &= anyfin
    idx = np.nonzero(sel)[0]
    out = {'row': idx, 'f4': f4[idx], 'd_km': d[idx], 'az_deg': az[idx], 'db_deg': db[idx], 'xt_km': xt[idx], 'dX_km': dx[idx], 'dH_km': dh[idx],
           'in_strip': masks['strip'][idx], 'in_X200': masks['X200'][idx], 'in_H200': masks['H200'][idx], 'acoustic_keep': keep[idx]}
    for c, v in side.items(): out[c] = v[idx]
    for c in KEEP_COLS:
        try: out[c] = g(c)[idx]
        except (KeyError, ValueError): pass
    for k in keys: out['lm|' + k] = lm[k][idx]
    for vn in VNAME: out['lnL|' + vn] = lnL[vn][idx]; out['z2|' + vn] = z2[vn][idx]
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(rows_path, **{k.replace('/', '_'): v for k, v in out.items()})
    res['stored_rows'] = int(len(idx)); res['acoustic_keep_rows'] = int(keep.sum())
    # best possible lnL in seed (diagnostic: how close any row gets, irrespective of weight)
    res['max_lnL'] = {vn: float(np.max(lnL[vn][anyfin])) for vn in VNAME}
    res['min_z2'] = {vn: float(np.min(z2[vn][anyfin])) for vn in VNAME}
    return res


def process_targeted(job):
    """Run J waypoints seed k with the selected parents' production children REPLACED by the targeted run's fresh children
    (targeted_build.py). Production rows keep end of flight's cells; targeted rows use the same cells with the seed normaliser
    of production (cells_t + ln W_t - ln W_prod), so the combined rows estimate exactly the quantities of the production seed."""
    k, P, K, eof_root, core_root, tgt_sd, sub_handoff, sel_json, rows_dir = job
    stratum = 'run-j-waypoints'
    sd = pathlib.Path(eof_root) / stratum / f'seed-{k}'
    cp, fp, gp = seed_cells(sd, pathlib.Path(core_root) / stratum / 'bto-bfo' / f'seed-{k}' / 'handoff-m0011' / 'handoff.npy')
    ct, ft, gt = seed_cells(pathlib.Path(tgt_sd), pathlib.Path(sub_handoff))
    sel = np.asarray(json.load(open(sel_json))['parents'], np.int64)
    Wp, Wt = gp('weight').sum(), gt('weight').sum()
    parp = gp('parent').astype(np.int64); keep = ~np.isin(parp, sel)
    c0 = float(np.log(P / K)); corr = float(np.log(Wt) - np.log(Wp))
    lm = {kk: np.r_[cp[kk][keep], ct[kk] + corr] + c0 for kk in KEYS}
    lnz_prod = {kk: lse(cp[kk] + c0) for kk in HEAD}
    del cp, ct
    f4 = np.r_[fp[keep], ft]; nt = len(ft)
    part = sel[gt('parent').astype(np.int64)]
    def g(name):
        if name == 'parent': return np.r_[parp[keep], part].astype(float)
        return np.r_[gp(name)[keep], gt(name)]
    tau_p = np.load(sd / 'tau90_v1.npz'); att = np.load(sd / 'attitude_v1.npz')
    tau_t = np.load(pathlib.Path(tgt_sd) / 'tau90_v1.npz')
    side = {c: np.r_[tau_p[c][keep], tau_t[c]] for c in ('tau90_s', 'energy_transferred_j', 'decel_g')}
    side.update({'bank_deg_att': np.r_[att['bank_deg'][keep], np.full(nt, np.nan, np.float32)],
                 'bank_source': np.r_[att['bank_source'][keep], np.full(nt, 255, np.uint8)],
                 'n_pulses': np.r_[att['n_pulses'][keep], np.zeros(nt, np.uint8)],
                 'targeted': np.r_[np.zeros(keep.sum(), bool), np.ones(nt, bool)]})
    res = analyse(lm, KEYS, HEAD, f4, g, side, pathlib.Path(rows_dir) / f'{stratum}-seed-{k}.npz')
    res.update({'stratum': stratum, 'seed': k, 'c0': c0, 'targeted': True, 'n_selected_parents': int(len(sel)), 'rows_replaced': int((~keep).sum()),
                'rows_targeted': int(nt), 'lnZ_prod': lnz_prod, 'lnZ_combined': {kk: lse(lm[kk]) for kk in HEAD}, 'W_prod': float(Wp), 'W_tgt': float(Wt),
                'W_prod_selected': float(gp('weight')[~keep].sum())})
    return res


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'targeted':
    import pickle
    k = int(sys.argv[2]); T = pathlib.Path(sys.argv[3])
    r = process_targeted((k, 0.9982, 24, '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j', '/Users/pete/Downloads/mh370-exchange/core/run-j',
                          T / f'compact-seed-{k}', T / 'RT' / 'bto-bfo' / f'seed-{1000 + k}' / 'handoff.npy',
                          T / 'RT' / 'bto-bfo' / f'seed-{1000 + k}' / 'selection.json', str(T / 'rows')))
    pickle.dump(r, open(T / f'res-seed-{k}.pkl', 'wb'))
    print('targeted seed', k, 'lnZ prod/comb D0', r['lnZ_prod'][HEAD[0]], r['lnZ_combined'][HEAD[0]], 'rows', r['rows_targeted'])
