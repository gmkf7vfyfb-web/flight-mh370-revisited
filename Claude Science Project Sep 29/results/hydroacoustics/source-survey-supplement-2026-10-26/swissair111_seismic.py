"""Swissair 111 (3 Sep 1998 01:31:18 UTC) impact: open seismic records, measurements, magnitude,
radiated seismic energy and seismic coupling (new class S1). EXPLORATORY. Returns nothing to the composer.
Data: Earthquakes Canada CNDC FDSN (network CN) and EarthScope FDSN (IU.HRV). Cached under work/.
Run from the workspace root:  python scripts/swissair111_seismic.py
"""
import os, io, time, subprocess, numpy as np, pandas as pd
from obspy import read, read_inventory, UTCDateTime
from obspy.geodetics import gps2dist_azimuth
from obspy.signal.trigger import recursive_sta_lta
from obspy.signal.filter import envelope
from scipy.signal.windows import dpss
os.makedirs('work/d3', exist_ok=True); os.makedirs('out', exist_ok=True)
CN = 'https://www.earthquakescanada.nrcan.gc.ca/fdsnws'; ES = 'https://service.earthscope.org/fdsnws'
LAT, LON = 44 + 24/60 + 33/3600, -(63 + 58/60 + 25/3600)   # TSB A98H0003 debris-field centre
T0 = UTCDateTime('1998-09-03T01:31:18')                    # TSB impact time (UTC date is 3 Sep)
SR = 40.0

def curl(url, fn, tries=6):
    for k in range(tries):
        if os.path.exists(fn) and os.path.getsize(fn) > 5000: return '200(cached)'
        code = subprocess.run(['curl', '-sL', '-m', '180', '-o', fn, '-w', '%{http_code}', url], capture_output=True, text=True).stdout
        if code != '503': return code
        time.sleep(8)
    return code

T = 'starttime=1998-09-03T01:15:00&endtime=1998-09-03T01:55:00'
fetch_log = {s: curl(f'{CN}/dataselect/1/query?network=CN&station={s}&{T}', f'work/d3/cn_{s}.mseed') for s in ['LMN', 'GSQ', 'GGN']}
fetch_log['HRV'] = curl(f'{ES}/dataselect/1/query?network=IU&station=HRV&channel=BH?&{T}', 'work/d3/es_HRV.mseed')
curl(f'{CN}/station/1/query?network=CN&station=LMN,GGN,GSQ&starttime=1998-09-01&endtime=1998-09-03&level=response', 'work/cn_LMN_resp.xml')
curl(f'{ES}/station/1/query?network=NE,IU&station=WVL,HRV&channel=HH?,BH?&starttime=1998-09-01&endtime=1998-09-03&level=response', 'work/es_resp.xml')
inv = read_inventory('work/cn_LMN_resp.xml') + read_inventory('work/es_resp.xml')
sta = {}
for n in inv:
    for s in n:
        d, az, baz = gps2dist_azimuth(LAT, LON, s.latitude, s.longitude); sta[s.code] = (s.latitude, s.longitude, d/1e3, az)
dkm = sta['LMN'][2]

def load(fn):
    s = read(fn); s.merge(fill_value=0)
    for tr in s:
        tr.detrend('demean'); tr.detrend('linear'); tr.taper(0.02); fs = tr.stats.sampling_rate
        tr.remove_response(inventory=inv, output='VEL', pre_filt=[0.3, 0.5, 0.45*fs, 0.48*fs], water_level=60)
    return s
def bp(tr, f1, f2, causal=False): return tr.copy().filter('bandpass', freqmin=f1, freqmax=f2, corners=4, zerophase=not causal)
def win(tr, a, b, ref):
    t = tr.times(reftime=ref); return tr.data[(t >= a) & (t < b)]
def aic_pick(x):
    n = len(x); k = np.arange(5, n-5)
    a = np.array([kk*np.log(np.var(x[:kk])+1e-30) + (n-kk-1)*np.log(np.var(x[kk:])+1e-30) for kk in k]); return k[np.argmin(a)]
def mtspec(x, dt, NW=3, K=5):
    tp = dpss(len(x), NW, K); X = np.fft.rfft(tp*(x-x.mean()), axis=1); return np.fft.rfftfreq(len(x), dt), (abs(X)**2).mean(0)*dt

lmn = load('work/d3/cn_LMN.mseed'); rows = []
def add(item, value, unit='', note=''): rows.append(dict(item=item, value=value, unit=unit, note=note))
add('impact time (TSB A98H0003)', '1998-09-03T01:31:18', 'UTC', 'TSB footnote 1: in UTC the flight occurred on 3 September 1998')
add('impact latitude', round(LAT, 5), 'deg', 'TSB debris-field centre 44 24 33 N'); add('impact longitude', round(LON, 5), 'deg', 'TSB 063 58 25 W')
add('water depth', 55, 'm', 'TSB'); add('main debris field', '125 x 95', 'm', 'TSB')
add('CN catalogue event', '19980903.0131003', '', 'origin 1998-09-03T01:31:17.0Z, epicentre fixed at wreck, depth 0 (operator assigned), event type "mining explosion", text "Swiss air crash flight 111"')
add('CN catalogue magnitude', 0.57, 'MwN (CN FDSN label; Canadian Nuttli-type MN)', 'CN catalogue creation time 2001-05-24')
add('ISC bulletin', 'no event', '', 'ISC FDSN event query 3 Sep 1998 00:00-24:00 UTC, 38-52 N 75-50 W, all origins: HTTP 204 (checked 24 Oct 2026)')
add('USGS ComCat', 'no event', '', '3 Sep 1998 00:30-03:00 UTC, 40-50 N 72-55 W: no rows (checked 24 Oct 2026)')
add('Halifax station HAL', 'no 1998 epoch in CNDC FDSN', '', 'HAL metadata start 2003-01-13 (EHZ); the 1998 Halifax seismograph record named by TSB is not in the open FDSN archive')
add('CN.GGN (Grand Manan, 240 km)', 'no data', '', f'CNDC dataselect HTTP {fetch_log["GGN"]} for the window')
for code in ['LMN', 'GSQ', 'GGN', 'HRV']:
    add(f'distance to {code}', round(sta[code][2], 1), 'km', f'azimuth from wreck {sta[code][3]:.1f} deg')
add('LMN instrument', 'Guralp CMG-3T, 40 sps BHZ/BHN/BHE', '', 'Caledonia Mountain NB; the TSB "Moncton" record is assumed to be this station (about 70 km SW of Moncton) - assumption')
# picks
picks = {}
for c in 'ZNE':
    tr = bp(lmn.select(channel='BH'+c)[0], 3, 15, causal=True); t = tr.times(reftime=T0)
    for ph, (a, b) in {'P': (15, 40), 'S': (42, 58)}.items():
        m = (t > a) & (t < b); picks[(c, ph)] = float(t[m][aic_pick(tr.data[m])])
for (c, ph), v in picks.items(): add(f'LMN {ph} onset BH{c} (AIC, 3-15 Hz causal)', round(v, 2), 's after 01:31:18')
tP = np.mean([picks[('Z', 'P')], picks[('N', 'P')]]); tS = np.mean([picks[(c, 'S')] for c in 'ZNE'])
add('S-P time', round(tS-tP, 2), 's'); add('S-P distance (Vp 6.0-6.3, Vs 3.5-3.65 km/s)', f'{(tS-tP)/(1/3.5-1/6.0):.0f}-{(tS-tP)/(1/3.65-1/6.3):.0f}', 'km', f'true distance {dkm:.1f} km')
o = [tP-dkm/v for v in (6.0, 6.3)] + [tS-dkm/v for v in (3.5, 3.65)]
add('origin time from LMN picks', f'{min(o):+.2f} to {max(o):+.2f}', 's relative to 01:31:18', 'crustal Vp 6.0-6.3, Vs 3.5-3.65 km/s; timing of 1998 digitiser clock not independently verified')
# amplitudes
NOISE, SIG, PW, SW = (-120, -5), (27.0, 75.0), (27.0, 47.5), (47.5, 75.0)
for f1, f2 in [(1, 3), (2, 8), (3, 15), (1.5, 18)]:
    for c in 'ZNE':
        tr = bp(lmn.select(channel='BH'+c)[0], f1, f2); n = win(tr, *NOISE, T0); s = win(tr, *SIG, T0)
        add(f'LMN BH{c} {f1}-{f2} Hz peak velocity', round(abs(s).max()*1e9, 2), 'nm/s', f'noise RMS {n.std()*1e9:.2f} nm/s; peak SNR {abs(s).max()/n.std():.1f}')
trs = [bp(lmn.select(channel='BH'+c)[0], 1.5, 18) for c in 'ZNE']
t1 = max(t.stats.starttime for t in trs); t2 = min(t.stats.endtime for t in trs)
for t in trs: t.trim(t1, t2, nearest_sample=True)
L = min(len(t.data) for t in trs); V = np.sqrt(sum(t.data[:L]**2 for t in trs)); tt = trs[0].times(reftime=T0)[:L]; m = (tt > SIG[0]) & (tt < SIG[1])
add('LMN 3-component vector PGV 1.5-18 Hz', round(V[m].max()*1e9, 2), 'nm/s', f'at {tt[m][V[m].argmax()]:.2f} s')
E2 = sum(envelope(bp(lmn.select(channel='BH'+c)[0], 3, 15).trim(t1, t2, nearest_sample=True).data[:L])**2 for c in 'ZNE')
Es_ = np.convolve(E2, np.ones(int(SR))/SR, 'same'); lev = np.median(Es_[(tt > NOISE[0]) & (tt < NOISE[1])])
for f in [2, 3]:
    i = np.where((Es_ > f*lev) & (tt > 20) & (tt < 101))[0]; add(f'signal duration (3-15 Hz power > {f}x noise median)', round(tt[i[-1]]-tt[i[0]], 1), 's', f'{tt[i[0]]:.1f} to {tt[i[-1]]:.1f} s')
raw = read('work/d3/cn_LMN.mseed'); glitch = []
for tr in raw:
    x = tr.copy(); x.detrend('linear'); x.filter('highpass', freq=2, zerophase=True); t = x.times(reftime=T0); mm = (t > 101.5) & (t < 103.5)
    glitch.append(float(t[mm][np.argmax(abs(x.data[mm]))]))
add('impulsive transient', f'{np.mean(glitch):.2f}', 's after 01:31:18', '2-sample impulse on all 3 components at the same sample, no dispersion or coda: probable instrumental glitch, excluded')
# third-octave band SNR
spec = {}
for c in 'ZNE':
    tr = lmn.select(channel='BH'+c)[0]
    for nm, (a, b) in {'noise': (-80, -30), 'P': (27, 47.5), 'S': (47.5, 75)}.items():
        f, S = mtspec(win(tr, a, b, T0), 1/SR); spec[(c, nm)] = (f, S/(b-a))
fc = 2**(np.arange(-3, 13)/3.); fc = fc[(fc >= 0.6) & (fc <= 17)]
def bpow(c, nm, f0):
    f, S = spec[(c, nm)]; mm = (f >= f0/2**(1/6)) & (f < f0*2**(1/6)); return S[mm].mean()
band = pd.DataFrame([dict(f_centre_Hz=round(f0, 2), amp_snr_P=np.sqrt(sum(bpow(c, 'P', f0) for c in 'ZNE')/sum(bpow(c, 'noise', f0) for c in 'ZNE')),
                          amp_snr_S=np.sqrt(sum(bpow(c, 'S', f0) for c in 'ZNE')/sum(bpow(c, 'noise', f0) for c in 'ZNE'))) for f0 in fc])
band.round(3).to_csv('out/swissair111-lmn-band-snr.csv', index=False)
i = band.amp_snr_S.idxmax(); add('S-window band SNR maximum', f'{band.amp_snr_S[i]:.2f} at {band.f_centre_Hz[i]} Hz', 'third-octave', 'P window maximum %.2f at %s Hz' % (band.amp_snr_P.max(), band.f_centre_Hz[band.amp_snr_P.idxmax()]))
add('water-layer quarter-wave frequency', round(1500/(4*55), 2), 'Hz', 'c/(4h) for 55 m; observed peak near 8 Hz is consistent but this is not tested (no co-located reference)')
# reference events and magnitude
paz_wa = {'poles': [-6.283+4.7124j, -6.283-4.7124j], 'zeros': [0j, 0j], 'gain': 1.0, 'sensitivity': 1.0}
refs = [('Swissair 111 impact', '1998-09-03T01:31:17', LAT, LON, 0.57, 'work/d3/cn_LMN.mseed'),
        ('Possible blast, Bridgewater NS', '1999-10-23T15:20:54', 44.6081, -64.8204, 2.07, 'work/d3/ref_199910231520.mseed'),
        ('Earthquake 36 km SE of Truro NS', '1999-04-02T14:34:25', 45.1990, -62.8517, 2.17, 'work/d3/ref_199904021434.mseed'),
        ('Possible blast, southern NB', '1995-12-07T19:27:50', 45.0136, -66.3486, 2.07, 'work/d3/ref_199512071927.mseed'),
        ('Blast, Oromocto NB', '1999-11-13T15:16:50', 45.6843, -66.5288, 1.67, 'work/d3/ref_199911131516.mseed'),
        ('Blast, 11 km S of Oromocto NB', '1999-07-15T16:49:35', 45.7541, -66.5225, 1.77, 'work/d3/ref_199907151649.mseed')]
edges = 2**np.arange(np.log2(1.5), np.log2(18)+1e-9, 0.5); RHO = 2700.
G = {'1/r': lambda R: 1/R, 'trilinear': lambda R: (1/R) if R <= 70e3 else ((1/70e3) if R <= 130e3 else (1/70e3)*np.sqrt(130e3/R))}
def energy(s, t0, d, gname, q0, eta, fs):
    r = d*1e3; W = {'P': (d/6.4-1, d/3.7-1, 6.1e3), 'S': (d/3.7-1, d/3.7-1+27.5, 3.5e3)}; Es = 0; bands = []
    for f1, f2 in zip(edges[:-1], edges[1:]):
        fcn = np.sqrt(f1*f2)
        for ph, (a, b, vel) in W.items():
            e = n = 0
            for c in 'ZNE':
                tr = bp(s.select(channel='BH'+c)[0], f1, f2); x = win(tr, a, b, t0); nz = win(tr, -120, -5, t0); e += (x**2).sum()/SR; n += nz.var()*len(x)/SR
            net = max(e-n, 0); bands.append((fcn, ph, e/n))
            Es += 4*np.pi*RHO*vel*net*np.exp(2*np.pi*fcn*r/(q0*fcn**eta*vel))*fs/G[gname](r)**2
    return Es, bands
MR = []
for lab, ts, la, lo, mag, fn in refs:
    if lab.startswith('Swissair'): s = lmn
    else:
        t0r = UTCDateTime(ts); curl(f'{CN}/dataselect/1/query?network=CN&station=LMN&starttime={(t0r-200).isoformat()}&endtime={(t0r+200).isoformat()}', fn); s = load(fn)
    t0 = UTCDateTime(ts); d = gps2dist_azimuth(la, lo, *sta['LMN'][:2])[0]/1e3
    a, b = d/3.7-1, d/3.0+5
    v15 = abs(win(bp(s.select(channel='BHZ')[0], 1, 15), a, b, t0)).max(); v315 = abs(win(bp(s.select(channel='BHZ')[0], 3, 15), a, b, t0)).max()
    amps = []
    for c in 'NE':
        tr = s.select(channel='BH'+c)[0].copy(); tr.integrate(); tr.filter('highpass', freq=0.5, corners=2, zerophase=True); tr.simulate(paz_remove=None, paz_simulate=paz_wa)
        amps.append(abs(win(tr, d/6.4-1, b, t0)).max()*1e9)
    R = np.hypot(d, 0 if lab.startswith('Swissair') else 5); D = d/111.195
    Es_c, _ = energy(s, t0, d, 'trilinear', 680, 0.36, 0.25)
    MR.append(dict(event=lab, origin_utc=ts, catalogue_MN=mag, dist_LMN_km=round(d, 1), Lg_peak_Z_1to15Hz_nm_s=v15*1e9, Lg_peak_Z_3to15Hz_nm_s=v315*1e9,
                   MN_formula_1to15Hz=3.30+1.66*np.log10(D)+np.log10(v15*1e6/(2*np.pi)), MN_formula_3to15Hz=3.30+1.66*np.log10(D)+np.log10(v315*1e6/(2*np.pi)),
                   WA_amp_nm=np.mean(amps), ML_HuttonBoore=np.log10(np.mean(amps))+1.11*np.log10(R)+0.00189*R-2.09,
                   Es_direct_central_J=Es_c, log10Es_minus_1p5MN=np.log10(Es_c)-1.5*mag))
MR = pd.DataFrame(MR); ref = MR.iloc[1:]
rel15 = ref.catalogue_MN + MR.MN_formula_1to15Hz.iloc[0] - ref.MN_formula_1to15Hz; rel315 = ref.catalogue_MN + MR.MN_formula_3to15Hz.iloc[0] - ref.MN_formula_3to15Hz
MR['impact_MN_relative_1to15Hz'] = [np.nan] + list(rel15); MR['impact_MN_relative_3to15Hz'] = [np.nan] + list(rel315)
MR.round(4).to_csv('out/swissair111-reference-events-lmn.csv', index=False)
add('impact MN relative to 5 reference events at LMN (1-15 Hz)', f'{rel15.mean():.2f} +/- {rel15.std():.2f}', 'MN', 'mean +/- SD over references; same station, same method')
add('impact MN relative to 5 reference events at LMN (3-15 Hz)', f'{rel315.mean():.2f} +/- {rel315.std():.2f}', 'MN')
add('Nuttli formula minus catalogue MN, reference events', f'{(ref.MN_formula_1to15Hz-ref.catalogue_MN).mean():.2f} +/- {(ref.MN_formula_1to15Hz-ref.catalogue_MN).std():.2f}', 'MN units', 'analyst-practice offset; impact offset %.2f' % (MR.MN_formula_1to15Hz.iloc[0]-0.57))
add('ML (Hutton-Boore, WA simulated, horizontals)', round(MR.ML_HuttonBoore.iloc[0], 2), 'ML', 'California attenuation; indicative only')
add('Mw estimate from MN', f'{0.57-0.5:.2f} to {rel15.mean()-0.5:.2f}', 'Mw', 'eastern Canada average MN - Mw = 0.5 (Bent 2011, as cited by Bent & Greene); not a moment measurement')
# energy grid
egrid = []
for gname in G:
    for q0, eta in [(680, 0.36), (893, 0.32), (500, 0.5)]:
        for fs in [0.25, 1.0]:
            Es, bands = energy(lmn, T0, dkm, gname, q0, eta, fs); egrid.append(dict(spreading=gname, Q=f'{q0} f^{eta}', free_surface_energy_factor=fs, Es_J=Es))
egrid = pd.DataFrame(egrid); egrid.to_csv('out/swissair111-energy-sensitivity.csv', index=False)
add('radiated seismic energy, direct, 1.5-17 Hz (12-case grid)', f'{egrid.Es_J.min():.3g} to {egrid.Es_J.max():.3g}', 'J', f'median {egrid.Es_J.median():.3g} J; band-limited, noise-subtracted; lower bound for full band')
c_ref = ref.log10Es_minus_1p5MN.mean()
add('reference calibration log10(Es) - 1.5 MN (same method, 5 land events)', f'{c_ref:.2f} +/- {ref.log10Es_minus_1p5MN.std():.2f}', '', 'impact value %.2f' % MR.log10Es_minus_1p5MN.iloc[0])
Mlist = [0.57, rel15.mean()]
gr = [10**(1.5*m+4.8) for m in Mlist]; grw = [10**(1.5*(m-0.5)+4.8) for m in Mlist]; cb = [10**(1.5*(m-0.5)+4.4) for m in Mlist]
add('Es from Gutenberg-Richter log Es = 1.5M + 4.8, M = MN', f'{min(gr):.3g} to {max(gr):.3g}', 'J', 'MN 0.57 (catalogue) to %.2f (relative)' % rel15.mean())
add('Es from Gutenberg-Richter with M = MN - 0.5', f'{min(grw):.3g} to {max(grw):.3g}', 'J')
add('Es from log Es = 1.5 Me + 4.4 (Choy-Boatwright form), Me = MN - 0.5', f'{min(cb):.3g} to {max(cb):.3g}', 'J')
# kinetic energy and coupling
KE = lambda m, kn: 0.5*m*(kn*0.514444)**2
KEc, KElo, KEhi = KE(230e3, 300), KE(215e3, 290), KE(230e3, 310)
add('impact kinetic energy', f'{KEc:.3g} (range {KElo:.3g} to {KEhi:.3g})', 'J', 'mass 230 t (crew-reported gross weight at 01:21) down to 215 t (assumed allowance: fuel dump began after 01:25:41 and stopped before impact, amount not established); speed 300 kn indicated (TSB), 290-310 kn assumed; IAS taken as TAS at sea level')
Esall = [egrid.Es_J.min(), egrid.Es_J.max(), min(gr+grw+cb), max(gr+grw+cb)]
add('seismic coupling class S1 = Es / KE, direct method', f'{egrid.Es_J.min()/KEhi:.2g} to {egrid.Es_J.max()/KElo:.2g}', '', 'NEW CLASS S1 (regional land seismic radiated energy over impact KE). Not comparable with hydroacoustic classes D1-D4 or the Arons definition (Brown et al. 2026 ~1e-4)')
add('seismic coupling class S1 = Es / KE, magnitude-energy relations', f'{min(gr+grw+cb)/KEhi:.2g} to {max(gr+grw+cb)/KElo:.2g}', '', 'earthquake-derived relations applied to a surface impact: indicative')
add('seismic coupling class S1, all methods', f'{min(Esall)/KEhi:.2g} to {max(Esall)/KElo:.2g}', '', 'provisional; spans about 3 orders of magnitude')
# detection statistics
def det(tr, f1, f2, a, b, exclude=(), ref=T0):
    x = bp(tr, f1, f2); fs = x.stats.sampling_rate; cft = recursive_sta_lta(x.data, int(fs), int(30*fs)); t = x.times(reftime=ref); Lw = b-a
    mm = (t >= a) & (t < b); stat = cft[mm].max(); tmax = t[mm][cft[mm].argmax()]; nulls = []; s0 = t[0]+60
    while s0+Lw < t[-1]:
        if not (s0 < b+60 and s0+Lw > a-60) and not any(s0 < e2 and s0+Lw > e1 for e1, e2 in exclude): nulls.append(cft[(t >= s0) & (t < s0+Lw)].max())
        s0 += Lw
    nulls = np.array(nulls); k = int((nulls >= stat).sum()); nz = x.data[(t >= -300) & (t < -5)]
    return dict(max_sta_lta=round(float(stat), 2), t_of_max_s=round(float(tmax), 1), snr_peak=round(float(abs(x.data[mm]).max()/nz.std()), 2), n_null=len(nulls), k_null_ge=k, p=round((k+1)/(len(nulls)+1), 4), p_floor=round(1/(len(nulls)+1), 4), noise_rms_nm_s=round(float(nz.std()*1e9), 3))
oth = load('work/d3/cn_GSQ.mseed') + load('work/d3/es_HRV.mseed')
D = []
D.append(dict(station='CN.LMN BHZ', target='P to Lg', band='3-15 Hz', dist_km=round(dkm, 1), **det(lmn.select(channel='BHZ')[0], 3, 15, dkm/6.4-3, dkm/3.0+15, exclude=[(99, 106)])))
for sc, f1, f2 in [('GSQ', 2, 10), ('HRV', 1, 8)]:
    tr = oth.select(station=sc).select(component='Z')[0]; d = sta[sc][2]
    r = det(tr, f1, f2, d/6.4-3, d/3.0+15)
    pred = 2*np.pi*10**(MR.MN_formula_1to15Hz.iloc[0]-3.30-1.66*np.log10(d/111.195))*1e3
    D.append(dict(station=f'{tr.stats.network}.{sc} {tr.stats.channel}', target='P to Lg', band=f'{f1}-{f2} Hz', dist_km=round(d, 1), **r, pred_Lg_peak_nm_s=round(pred, 2), pred_snr=round(pred/r['noise_rms_nm_s'], 2)))
for c in 'ZNE':
    for f1, f2 in [(1, 15), (3, 15)]:
        D.append(dict(station=f'CN.LMN BH{c}', target='air-coupled arrival 0.31-0.35 km/s', band=f'{f1}-{f2} Hz', dist_km=round(dkm, 1), **det(lmn.select(channel='BH'+c)[0], f1, f2, dkm/0.35, dkm/0.31, exclude=[(0, 110)])))
D = pd.DataFrame(D); D['rank_by_p'] = D.p.rank(method='min').astype(int); D['likelihood_ratio'] = 'not computed (no calibrated signal model for STA/LTA maxima)'
D.to_csv('out/swissair111-detection-tests.csv', index=False)
pd.DataFrame(rows).to_csv('out/swissair111-seismic.csv', index=False)
np.savez('work/swissair_fig_inputs.npz', dkm=dkm, picks=np.array([[picks[(c, p)] for p in 'PS'] for c in 'ZNE']), glitch=np.mean(glitch))
print(pd.DataFrame(rows).to_string()); print(D.to_string())
