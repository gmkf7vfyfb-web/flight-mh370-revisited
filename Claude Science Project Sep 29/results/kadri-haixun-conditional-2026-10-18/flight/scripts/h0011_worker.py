"""Parse one run J m0011 hand-off (handoff.toml.gz), extrapolate each row in cruise to
00:19:29 / 00:19:37, and compute BTO/BFO residuals at 00:10:59, 00:19:29 (R600 log-on) and
00:19:37 with the engine's forward model (report/satcom_model.py equations, vectorised)."""
import gzip, sys, math, numpy as np, os
ENG = os.environ['ENG']
sys.path.insert(0, ENG + '/report')
import satcom_model as sm

T11, T19A, T19B = 1394237459.0, 1394237969.0, 1394237977.0
KEYS = {  # (section, key) -> column
 ('row','weight'):'weight', ('row','mode'):'mode', ('row','log_correction'):'logc', ('row','origin'):'origin',
 ('row.bias','mean_hz'):'bias', ('row.bias','variance_hz2'):'biasvar',
 ('row.aircraft','lat'):'lat', ('row.aircraft','lon'):'lon', ('row.aircraft','alt_ft'):'alt',
 ('row.aircraft','alt_target_ft'):'alt_t', ('row.aircraft','mach'):'mach', ('row.aircraft','control'):'control',
 ('row.aircraft','turn_remaining'):'turn_rem', ('row.aircraft','v_north_kt'):'vn', ('row.aircraft','v_east_kt'):'ve',
 ('row.aircraft','turns'):'turns', ('row.aircraft','climbs'):'climbs', ('row.aircraft','accelerations'):'accels',
 ('row.aircraft','turned_rad'):'turned', ('row.aircraft','next_turn'):'next_turn', ('row.aircraft','next_climb'):'next_climb',
 ('row.aircraft','fuel_kg'):'fuel', ('row.aircraft','fuel_exhausted_unix_s'):'fuel_ex', ('row.aircraft','declination_rad'):'decl',
 ('row.aircraft','wind_error_north_kt'):'wen', ('row.aircraft','wind_error_east_kt'):'wee',
 ('row.aircraft.weather','wind_north_kt'):'wn', ('row.aircraft.weather','wind_east_kt'):'we',
 ('row.aircraft.weather','temperature_k'):'temp',
 ('row.aircraft.tanks','driftdown_fpm'):'dd_fpm', ('row.aircraft.tanks','left_exhausted_unix_s'):'lex', ('row.aircraft.tanks','right_exhausted_unix_s'):'rex',
 ('row.aircraft.tanks','left_kg'):'lkg', ('row.aircraft.tanks','right_kg'):'rkg',
}
COLS = sorted(set(KEYS.values())) + ['amode']
AMODES = {'TrueHeading':0,'MagneticHeading':1,'TrueTrack':2,'MagneticTrack':3,'Lnav':4,'LateralNavigation':4}

def parse(path):
    rows = []; cur = None; sec = None
    with gzip.open(path, 'rt') as f:
        for line in f:
            if line[0] == '[':
                s = line.strip()
                if s == '[[row]]':
                    if cur is not None: rows.append(cur)
                    cur = dict.fromkeys(COLS, np.nan); sec = 'row'
                else: sec = s.strip('[]')
                continue
            if cur is None or ' = ' not in line: continue
            k, v = line.split(' = ', 1)
            col = KEYS.get((sec, k))
            if col is not None:
                v = v.strip()
                cur[col] = float(v) if v not in ('nan', 'inf', '-inf', 'true', 'false') else (float(v) if v in ('nan','inf','-inf') else float(v=='true'))
            elif sec == 'row.aircraft' and k == 'mode':
                cur['amode'] = AMODES.get(v.strip().strip('"'), -1)
    if cur is not None: rows.append(cur)
    return {c: np.array([r[c] for r in rows]) for c in COLS}

R = 6371.0088 / 1.852  # nm, spherical (route geometry only)
def dest(lat, lon, brg, d_nm):
    a, b, dr = np.radians(lat), np.radians(lon), d_nm / sm.R_NM
    la = np.arcsin(np.sin(a)*np.cos(dr) + np.cos(a)*np.sin(dr)*np.cos(brg))
    lo = b + np.arctan2(np.sin(brg)*np.sin(dr)*np.cos(a), np.cos(dr) - np.sin(a)*np.sin(la))
    back = np.arctan2(np.sin(b - lo)*np.cos(a), np.cos(la)*np.sin(a) - np.sin(la)*np.cos(a)*np.cos(b - lo))
    return np.degrees(la), np.degrees(lo), (np.degrees(back) + 180.0) % 360
def ecef(lat, lon, hkm):
    la, lo = np.radians(lat), np.radians(lon)
    n = sm.A / np.sqrt(1 - sm.E2*np.sin(la)**2)
    return np.stack([(n+hkm)*np.cos(la)*np.cos(lo), (n+hkm)*np.cos(la)*np.sin(lo), (n*(1-sm.E2)+hkm)*np.sin(la)], -1)
def bto(t, lat, lon, alt):
    sat, _ = sm.satstate(t)
    a = ecef(lat, lon, alt*sm.KM_FT)
    return 2*(np.linalg.norm(sat - a, axis=-1) + np.linalg.norm(sat - sm.GES))/sm.C*1e6 - sm.OFFSET
def bfo_nb(t, lat, lon, alt, vn, ve, vs):
    sat, satv = sm.satstate(t)
    la, lo = np.radians(lat), np.radians(lon)
    n = np.stack([-np.sin(la)*np.cos(lo), -np.sin(la)*np.sin(lo), np.cos(la)], -1)
    e = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
    hv = n*(vn*sm.KMS_KT)[:,None] + e*(ve*sm.KMS_KT)[:,None]
    a = ecef(lat, lon, alt*sm.KM_FT); up = ecef(lat, lon, alt*sm.KM_FT + 1.0) - a
    v = hv + up/np.linalg.norm(up, axis=-1, keepdims=True)*(vs*sm.KM_FT/60)[:,None]
    u = (sat - a)/np.linalg.norm(sat - a, axis=-1, keepdims=True)
    uplink = -sm.UP/sm.C*np.einsum('ij,ij->i', satv - v, u)
    g = (sat - sm.GES)/np.linalg.norm(sat - sm.GES); down = -sm.DOWN/sm.C*np.dot(satv, g)
    nom = sm.ecef(0, 64.5, 36210.12); s = ecef(lat, lon, np.zeros_like(lat))
    cu = (s - nom)/np.linalg.norm(s - nom, axis=-1, keepdims=True)
    comp = sm.UP/sm.C*np.einsum('ij,ij->i', hv, cu)
    return uplink + down + comp + sm.afc(t)

CLIMB_FPS = 66.66666666666667
def isa_p(ft):
    h = ft*0.3048
    return np.where(h <= 11000.0, 101325.0*np.clip(1 - 2.25577e-5*h, 1e-9, None)**5.25588, 22632.06*np.exp(-1.576883e-4*(h - 11000.0)))
def vs_fpm(d, alt):
    """Engine Aircraft::vertical_speed_fpm: one-engine hold-taper drift-down (run J fuel config:
    L/D 20.7, min-drag factor 1.038, exponent 0.864, level-off 30 fpm, ceiling = alt target),
    else +/- the 4,000 ft/min level-change rate, else 0."""
    one = (d['lkg'] > 0) != (d['rkg'] > 0)
    tas = d['mach']*np.sqrt(1.4*287.05287*d['temp'])/0.5144444444444445
    rod = tas*(1852.0/0.3048/60.0)/20.7*(1 - 1.038*(isa_p(alt)/isa_p(d['alt_t']))**0.864)
    dd = one & (d['alt_t'] < alt) & (rod >= 30.0)
    lvl = np.where(np.abs(d['alt_t'] - alt) < 1e-6, 0.0, np.sign(d['alt_t'] - alt)*CLIMB_FPS*60)
    return np.where(dd, -rod, lvl), dd
def at(d, t):
    """Cruise extrapolation from 00:10:59: constant ground velocity on a great circle, altitude
    moving to its target at the model climb rate."""
    dt = t - T11
    gs = np.hypot(d['vn'], d['ve']); brg = np.arctan2(d['ve'], d['vn'])
    la, lo, trk = dest(d['lat'], d['lon'], brg, gs*dt/3600)
    v0, _ = vs_fpm(d, d['alt'])
    dz = d['alt_t'] - d['alt']; step = np.sign(dz)*np.minimum(np.abs(dz), np.abs(v0)/60*dt)
    alt = d['alt'] + step
    vs = np.where(np.abs(dz) > np.abs(v0)/60*dt + 1e-6, v0, 0.0)
    # velocity re-expressed in the local frame at the new point (great-circle track)
    tr = np.radians(trk)
    return la, lo, alt, gs*np.cos(tr), gs*np.sin(tr), vs, np.degrees(np.arctan2(np.sin(tr), np.cos(tr))) % 360

def main(path, out):
    d = parse(path)
    vs11, dd = vs_fpm(d, d['alt']); d['one_engine_dd'] = dd.astype(float)
    d['bto11_res'] = 18040.0 - bto(T11, d['lat'], d['lon'], d['alt'])
    d['bfo11_res'] = 252.0 - (bfo_nb(T11, d['lat'], d['lon'], d['alt'], d['vn'], d['ve'], vs11) + d['bias'])
    d['vs11'] = vs11
    for tag, t in (('19a', T19A), ('19b', T19B)):
        la, lo, alt, vn, ve, vs, trk = at(d, t)
        d[f'lat{tag}'], d[f'lon{tag}'], d[f'alt{tag}'], d[f'trk{tag}'] = la, lo, alt, trk
        d[f'bto{tag}_res'] = (18400.0 if tag == '19a' else 18380.0) - bto(t, la, lo, alt)
        d[f'bfo{tag}_pred'] = bfo_nb(t, la, lo, alt, vn, ve, vs) + d['bias']
    d['bfo19a_res'] = 182.0 - d['bfo19a_pred']
    np.savez_compressed(out, **{k: v.astype(np.float64) for k, v in d.items()})
    print(out, len(d['lat']))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
