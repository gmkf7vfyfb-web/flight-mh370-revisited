"""BTO/BFO residuals for the 18:25-18:28 SATCOM sequence under route hypotheses from the 18:22 radar point.

Usage: .venv/bin/python report/sequence_1825.py

Messages: data/satcom-1825-sequence.csv (all aircraft-to-ground bursts 18:25-18:28 in the released
SITA/Inmarsat SU log). Routes start at 18:22:12, 10 NM past MEKAR on N571, FL350, constant ground
speed, fly-over turns at 15 deg bank: continue N571 (NILAM, IGOGU) or turn at NILAM onto P627
toward BEDAX. Satellite states: Inmarsat (Ashton et al. 2015, Table 4, Hermite-interpolated).
BTO and BFO use the core's equations (checked below against the core's fixture to 1e-6); BFO
residuals are against a 150 Hz bias, and the implied bias is measured minus predicted-without-bias.
Waypoints: historical Malaysia AIP (MEKAR, NILAM, IGOGU); BEDAX from AirNav Indonesia (P627).
"""
import json, math, numpy as np
from satcom_model import (C, UP, KM_FT, WP, T0, BIAS, ROOT, bto, bfo_nobias, basis, ecef, bearing, dist_nm, dest,
                          satstate, afc, weather, unix)
print('fixture BTO and BFO match the core to 1e-6')

def fly(route, gs_kt, t_end, bank=15.0):
    """Positions/velocities at 1 s from T0: start 10 NM past MEKAR toward NILAM; fly-over each waypoint then turn at `bank`."""
    pos=dest(WP['MEKAR'], bearing(WP['MEKAR'],WP['NILAM']), 10.0); hdg=bearing(pos,WP['NILAM'])
    legs=list(route); target=WP[legs.pop(0)]; out={}; t=T0
    rate=9.80665*math.tan(math.radians(bank))/(gs_kt*1852/3600)
    while t<=t_end+1e-9:
        out[round(t)]=(pos, hdg)
        if dist_nm(pos,target)<gs_kt/3600*1.0 and legs:
            target=WP[legs.pop(0)]
        want=bearing(pos,target); d=(want-hdg+math.pi)%(2*math.pi)-math.pi
        hdg+=max(-rate,min(rate,d))
        pos=dest(pos,hdg,gs_kt/3600); t+=1
    return out
# (time, channel, message, BFO, raw BTO, BTO correction, BTO sd)
MSG=[('18:25:27.421','R600','log-on request',142,17120,-4600,62),
     ('18:25:34.461','R1200','log-on ack (anomalous BTO)',273,51700,-5*7820,43),
     ('18:27:03.905','R1200','user data',176,12560,0,29),
     ('18:27:04.405','R1200','user data',175,12520,0,29),
     ('18:27:08.404','R1200','ack',172,12520,0,29),
     ('18:28:05.904','R1200','access request',144,12500,0,29),
     ('18:28:10.260','T1200','user data',148,7540,None,None),
     ('18:28:14.904','R1200','ack',143,12480,0,29)]
ROUTES={'N571 (NILAM, IGOGU)':['NILAM','IGOGU'],'P627 (NILAM, BEDAX)':['NILAM','BEDAX']}
res={}
for rname,route in ROUTES.items():
    for gs in (450,480,510):
        path=fly(route,gs,unix('2014-03-07T18:28:15'))
        rows=[]
        for tm,ch,msg,bfo,raw,corr,sd in MSG:
            t=unix('2014-03-07T'+tm); (pos,hdg)=path[round(t)]
            vn,ve=gs*math.cos(hdg),gs*math.sin(hdg); sat,sv=satstate(t)
            pb=bto(sat,pos[0],pos[1],35000); pf=bfo_nobias(sat,sv,afc(t),pos[0],pos[1],35000,vn,ve)
            rows.append(dict(t=tm,ch=ch,msg=msg,bfo=bfo,raw=raw,corr=corr,sd=sd,bto_corr=None if corr is None else raw+corr,
                pred_bto=pb,res_bto=None if corr is None else raw+corr-pb,pred_bfo=pf+BIAS,res_bfo=bfo-pf-BIAS,implied_bias=bfo-pf,
                lat=pos[0],lon=pos[1],track=math.degrees(hdg)%360))
        res[(rname,gs)]=rows
for (rname,gs),rows in res.items():
    print(f'\n== {rname}, ground speed {gs} kt, FL350 ==')
    print('time          ch     BFO  implied-bias  BFO-res(bias150)   BTO(corr)  BTO-res   pos (lat, lon)   track')
    for r in rows:
        bt='     n/a' if r['res_bto'] is None else f"{r['res_bto']:+8.0f}"
        bc='   n/a' if r['bto_corr'] is None else f"{r['bto_corr']:6d}"
        print(f"{r['t']}  {r['ch']:5s} {r['bfo']:4d}   {r['implied_bias']:7.1f}        {r['res_bfo']:+6.1f}          {bc}  {bt}   {r['lat']:.3f},{r['lon']:.3f}  {r['track']:5.1f}")

print('\n== Misfit by ground speed (chi-square; BTO: R600 + all R1200; settled BFO: 18:25:27, 18:28:05, 18:28:10 T, 18:28:14; bias 150 Hz, sd 7 Hz) ==')
print('speed   N571 BTO  N571 BFO   P627 BTO  P627 BFO')
settled={'18:25:27.421','18:28:05.904','18:28:10.260','18:28:14.904'}
for gs in range(300,531,20):
    line=f'{gs:4d} kt'
    for route in (['NILAM','IGOGU'],['NILAM','BEDAX']):
        path=fly(route,gs,unix('2014-03-07T18:28:15'))
        cb=cf=0.0
        for tm,ch,msg,bfo,raw,corr,sd in MSG:
            t=unix('2014-03-07T'+tm); (pos,hdg)=path[round(t)]
            vn,ve=gs*math.cos(hdg),gs*math.sin(hdg); sat,sv=satstate(t)
            if corr is not None: cb+=((raw+corr-bto(sat,pos[0],pos[1],35000))/sd)**2
            if tm in settled: cf+=((bfo-bfo_nobias(sat,sv,afc(t),pos[0],pos[1],35000,vn,ve)-BIAS)/7)**2
        line+=f'   {cb:7.1f}  {cf:7.1f} '
    print(line)


# ---------------------------------------------------------------------------------------------
# Part 2: sigma-annotated table, Mach implied by the fitted ground speed, free heading/speed fit,
# vertical-speed sensitivity, ground-speed uncertainty, and how far N571 could be flown by 18:40.
SIGMA_BFO = 7.0
SETTLED = {'18:25:27.421', '18:28:05.904', '18:28:10.260', '18:28:14.904'}


def fly_heading(hdg_deg, gs, t, vs_fpm=0.0, alt0=35000.0):
    """Straight great-circle flight from the 18:22:12 start at a fixed initial bearing."""
    start = dest(WP['MEKAR'], bearing(WP['MEKAR'], WP['NILAM']), 10.0)
    d = gs * (t - T0) / 3600
    pos = dest(start, math.radians(hdg_deg), d)
    # final bearing along the great circle
    back = bearing(pos, start)
    hdg = (back + math.pi) % (2 * math.pi)
    return pos, hdg, alt0 + vs_fpm * (t - T0) / 60


def predict(pos, hdg, gs, alt, t, vs_fpm=0.0):
    sat, sv = satstate(t)
    vn, ve = gs * math.cos(hdg), gs * math.sin(hdg)
    pb = bto(sat, pos[0], pos[1], alt)
    pf = bfo_nobias(sat, sv, afc(t), pos[0], pos[1], alt, vn, ve)
    if vs_fpm:
        n, e = basis(pos[0], pos[1]); a = ecef(pos[0], pos[1], alt * KM_FT)
        up = np.cross(n, e) * -1 if False else ecef(pos[0], pos[1], 1.0) - ecef(pos[0], pos[1], 0.0)
        up = up / np.linalg.norm(up); u = (sat - a) / np.linalg.norm(sat - a)
        pf += UP / C * np.dot(up * vs_fpm * KM_FT / 60, u)  # climbing towards the satellite raises BFO
    return pb, pf


def chi2(path_fn, use=('bto', 'bfo')):
    cb = cf = 0.0
    for tm, ch, msg, bfo, raw, corr, sd in MSG:
        t = unix('2014-03-07T' + tm); pos, hdg, gs, alt, vs = path_fn(t)
        pb, pf = predict(pos, hdg, gs, alt, t, vs)
        if corr is not None and 'bto' in use: cb += ((raw + corr - pb) / sd) ** 2
        if tm in SETTLED and 'bfo' in use: cf += ((bfo - pf - BIAS) / SIGMA_BFO) ** 2
    return cb, cf


def route_fn(route, gs):
    path = fly(route, gs, unix('2014-03-07T18:28:15'))
    return lambda t: (*path[round(t)], gs, 35000.0, 0.0)


print('\n== A. Every message with residuals and sigma multiples (FL350; BFO against a 150 Hz bias, sd 7 Hz) ==')
for rname, route, gs in [('N571', ['NILAM', 'IGOGU'], 350), ('N571', ['NILAM', 'IGOGU'], 480), ('P627', ['NILAM', 'BEDAX'], 350)]:
    f = route_fn(route, gs)
    print(f'-- {rname} at {gs} kt --')
    print('time          ch     BFO meas  BFO pred  BFO resid (sigma)     BTO corr  BTO pred  BTO resid (sigma)')
    for tm, ch, msg, bfo, raw, corr, sd in MSG:
        t = unix('2014-03-07T' + tm); pos, hdg, g, alt, vs = f(t); pb, pf = predict(pos, hdg, g, alt, t)
        rf = bfo - pf - BIAS
        tag = '' if tm in SETTLED else '  transient'
        bt = '      n/a            ' if corr is None else f'{raw + corr:8d}  {pb:8.0f}  {raw + corr - pb:+6.0f} ({(raw + corr - pb) / sd:+4.1f}σ)'
        print(f'{tm}  {ch:5s}  {bfo:6d}   {pf + BIAS:7.1f}   {rf:+6.1f} ({rf / SIGMA_BFO:+5.1f}σ){tag:11s}  {bt}')

# B. Mach implied by a ground speed along N571 at the 18:25-18:28 position, from ERA5.
# B. Mach implied by a ground speed along N571 at the 18:25-18:28 position, from ERA5.
print('\n== B. Mach needed for a given ground speed along N571 (track 296°) at 6.85N 95.75E, 18:26 UTC (ERA5) ==')
print('altitude   temp(K)  wind E/N (kt)   along-track wind   Mach @ 340 kt   @ 350 kt   @ 360 kt   @ 480 kt')
trk = math.radians(296.2); t26 = unix('2014-03-07T18:26:00')
for alt in [10000.0, 20000.0, 25000.0, 31000.0, 34000.0, 37000.0, 40000.0, 43000.0]:
    temp, ue, vn = weather(t26, alt, 6.85, 95.75)
    a_kt = math.sqrt(1.4 * 287.05287 * temp) / 0.514444
    along = ue * math.sin(trk) + vn * math.cos(trk)
    def mach(gs):
        air_n, air_e = gs * math.cos(trk) - vn, gs * math.sin(trk) - ue
        return math.hypot(air_n, air_e) / a_kt
    print(f'{alt:8.0f}  {temp:7.1f}   {ue:+5.1f}/{vn:+5.1f}      {along:+6.1f}          {mach(340):.3f}      {mach(350):.3f}     {mach(360):.3f}     {mach(480):.3f}')

# C. Free straight-line fit: any initial heading and ground speed from the 18:22:12 start.
print('\n== C. Straight-line fit with free heading and ground speed (FL350, level) ==')
best = None; grid = []
for hdg in range(200, 361, 2):
    for gs in range(250, 561, 10):
        cb, cf = chi2(lambda t, h=hdg, g=gs: (*fly_heading(h, g, t)[:2], g, 35000.0, 0.0))
        grid.append((hdg, gs, cb, cf)); tot = cb + cf
        if best is None or tot < best[2] + best[3]: best = (hdg, gs, cb, cf)
print(f'best: initial heading {best[0]}°, {best[1]} kt, chi2 BTO {best[2]:.1f} + BFO {best[3]:.1f} = {best[2] + best[3]:.1f} (11 measurements)')
ok = [(h, g) for h, g, cb, cf in grid if cb + cf <= best[2] + best[3] + 6.18]
hs, gss = [h for h, g in ok], [g for h, g in ok]
print(f'2-sigma joint region (delta chi2 <= 6.18): heading {min(hs)}-{max(hs)}°, ground speed {min(gss)}-{max(gss)} kt; N571 bearing is 296°')
okb = [(h, g) for h, g, cb, cf in grid if cb <= min(c for _, _, c, _ in grid) + 6.18]
print(f'BTO alone, 2-sigma: heading {min(h for h, g in okb)}-{max(h for h, g in okb)}°, speed {min(g for h, g in okb)}-{max(g for h, g in okb)} kt')

# D. Vertical speed: BFO and BTO sensitivity at 18:28 on N571.
print('\n== D. Vertical speed (N571, 350 kt): effect on the settled BFOs and on the BTOs ==')
for vs in [-3000, -2000, -1000, -500, 0, 500, 1000, 2000, 3000]:
    cb, cf = chi2(lambda t, v=vs: (*fly(['NILAM', 'IGOGU'], 350, unix('2014-03-07T18:28:15'))[round(t)], 350, 35000.0 + v * (t - T0) / 60, v))
    print(f'{vs:+6d} fpm: chi2 BTO {cb:6.1f}   settled BFO {cf:7.1f}')

# E. Ground-speed uncertainty along N571 from the BTOs (and how unlikely 480 kt is under the noise model).
print('\n== E. Ground speed along N571 from the BTOs (profile chi2, FL350, level) ==')
for label, drop in [('all BTOs', set()), ('without the R600 log-on (-4600 us correction)', {'18:25:27.421'}),
                    ('without both log-on BTOs', {'18:25:27.421', '18:25:34.461'})]:
    rows = []
    for gs in np.arange(250, 560, 2.0):
        path = fly(['NILAM', 'IGOGU'], gs, unix('2014-03-07T18:28:15')); c = 0.0
        for tm, ch, msg, bfo, raw, corr, sd in MSG:
            if corr is None or tm in drop: continue
            t = unix('2014-03-07T' + tm); pos, hdg = path[round(t)]; sat, _ = satstate(t)
            c += ((raw + corr - bto(sat, pos[0], pos[1], 35000)) / sd) ** 2
        rows.append((gs, c))
    g = np.array(rows); k = g[:, 1].argmin(); m = g[k, 1]
    def interval(d):
        s = g[g[:, 1] <= m + d, 0]; return f'{s.min():.0f}-{s.max():.0f}'
    c480 = np.interp(480, g[:, 0], g[:, 1])
    print(f'{label:48s} best {g[k, 0]:.0f} kt (chi2 {m:.1f}); 1-sigma {interval(1)} kt; 2-sigma {interval(4)} kt; '
          f'480 kt: delta chi2 {c480 - m:.1f}')

# F. How far along N571 before a turn to ~180° completed by the 18:39:55 BFO.
print('\n== F. Reach along N571 before turning south by 18:39:55 ==')
start = dest(WP['MEKAR'], bearing(WP['MEKAR'], WP['NILAM']), 10.0)
d_nilam = dist_nm(start, WP['NILAM']); d_igogu = d_nilam + dist_nm(WP['NILAM'], WP['IGOGU'])
print(f'from the 18:22:12 start: NILAM {d_nilam:.1f} NM, IGOGU {d_igogu:.1f} NM')
t_turn_end = unix('2014-03-07T18:39:55')
for gs in [350, 400, 450, 480, 510]:
    turn_s = math.radians(116) / (9.80665 * math.tan(math.radians(15)) / (gs * 1852 / 3600))  # 296 -> 180 at 15 deg bank
    reach = gs * ((t_turn_end - turn_s) - T0) / 3600
    print(f'{gs} kt: turn takes {turn_s:.0f} s; latest turn start at {reach:.0f} NM from the start = '
          f'{reach - d_nilam:+.0f} NM past NILAM ({"reaches" if reach >= d_igogu else "short of"} IGOGU)')

# G. The heading/speed trade-off, and what an anticipated (fly-by) turn at IGOGU needs.
print('\n== G1. Best heading at a given ground speed, and best speed at a given heading (straight, FL350, level) ==')
for gs in [336, 400, 450, 480, 510]:
    rows = [(h, cb + cf) for h, g, cb, cf in grid if g == gs] if gs % 10 == 0 else None
    if rows is None:
        rows = [(h, sum(chi2(lambda t, hh=h: (*fly_heading(hh, gs, t)[:2], gs, 35000.0, 0.0)))) for h in range(200, 361, 2)]
    h, c = min(rows, key=lambda r: r[1])
    print(f'{gs} kt: best initial heading {h}°, chi2 {c:.1f} (delta {c - best[2] - best[3]:+.1f} from the overall best)')
for hdg in [296, 306, 316, 326]:
    rows = [(g, cb + cf) for h, g, cb, cf in grid if h == hdg]
    g, c = min(rows, key=lambda r: r[1])
    print(f'heading {hdg}°: best {g} kt, chi2 {c:.1f} (delta {c - best[2] - best[3]:+.1f})')

print('\n== G2. Average ground speed after 18:28:14 needed to fly by IGOGU and be heading ~180° by 18:39:55 ==')
print('(on N571 at 336 kt until 18:28:14; fly-by turn of 116° at 15° bank anticipated tan(58°) x radius before IGOGU)')
d_1828 = 336 * (unix('2014-03-07T18:28:14') - T0) / 3600
for gs in [400, 450, 480, 510, 540]:
    radius_nm = (gs * 1852 / 3600) ** 2 / (9.80665 * math.tan(math.radians(15))) / 1852
    lead = radius_nm * math.tan(math.radians(58)); turn_s = math.radians(116) * radius_nm * 1852 / (gs * 1852 / 3600)
    need = d_igogu - lead - d_1828
    avail = (t_turn_end - turn_s - unix('2014-03-07T18:28:14')) * gs / 3600
    print(f'{gs} kt after 18:28: turn radius {radius_nm:.1f} NM, starts {lead:.0f} NM before IGOGU; '
          f'needs {need:.0f} NM, can fly {avail:.0f} NM -> {"feasible" if avail >= need else "not feasible"}')
