"""Analysis of the arrival-time tables written by arrivals_timing.py (deskstar, extended-window run, 84 release points, 16 or 32 ocean samples per model).
Writes tables to arr/tables/. All averages over ocean samples are plain means (equal weight, as in the module); the two ocean models have equal weight.
Core weights: res-smooth/wnode_df.npy (ruled core, final end of flight, Davey model + fuel, D0; weight per release point)."""
import numpy as np, pandas as pd, os, datetime as dt
os.makedirs('arr-high/tables', exist_ok=True)
RELEASE = 1394237977.0
def day(iso, end=False): return (dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc).timestamp() - RELEASE) / 86400.0 + (1.0 if end else 0.0)
BIN = 5.0; NB = 212; TC = (np.arange(NB) + 0.5) * BIN; DAYS = np.arange(0, 1060)
l = np.load('res-smooth/lm-head-s31.npz'); LAT, LON = l['lat'], l['lon']; W = np.load('res-smooth/wnode_df.npy'); W = W / W.sum()
M = {m: np.load(f'arr-high/arrivals-timing-{m}.npz', allow_pickle=True) for m in ('globcurrent', 'glorys12')}
ITEMS = [str(x) for x in M['globcurrent']['items']]
FIND = {'reunion-right-flaperon': '2015-07-29', 'mossel-bay-engine-cowling-roy': '2015-12-23', 'paindane-right-flap-fairing': '2015-12-27', 'vilanculos-horizontal-stabilizer-panel': '2016-02-28',
        'mauritius-left-outboard-flap': '2016-05-10', 'rodrigues-door-closet-panel': '2016-03-30', 'chidenguele-right-fan-cowling': '2016-04-24', 'antsiraka-cabin-interior-panel': '2016-06-12',
        'pemba-right-outboard-flap': '2016-06-23', 'linga-linga-vertical-stabilizer': '2016-08-26', 'nautilus-bay-right-aileron': '2016-12-23', 'mpame-right-flap-fairing': '2017-01-27'}
# node index of every row
def node_index(z):
    idx = np.empty(len(z['lat']), int)
    for r in range(len(idx)):
        d = (LAT - z['lat'][r]) ** 2 + (LON - z['lon'][r]) ** 2; idx[r] = int(d.argmin()); assert d.min() < 1e-8, (z['lat'][r], z['lon'][r])
    return idx
NI = {m: node_index(M[m]) for m in M}
def node_mean(m, arr):         # mean over ocean samples for each of the 84 nodes -> (84, ...)
    out = np.zeros((84,) + arr.shape[1:]); n = np.zeros(84)
    for r, i in enumerate(NI[m]): out[i] += arr[r]; n[i] += 1
    return out / n.reshape((84,) + (1,) * (arr.ndim - 1)), n
H = {}; A60 = {}; A9 = {}; AM = {}; SEG = {}
for m in M:
    H[m], nenv = node_mean(m, M[m]['hist'].astype(float)); A60[m], _ = node_mean(m, M[m]['a60']); A9[m], _ = node_mean(m, M[m]['a9']); AM[m], _ = node_mean(m, M[m]['amar'][:, None]); SEG[m], _ = node_mean(m, M[m]['seg'].astype(float))
    print(m, 'ocean samples per node: min', int(nenv.min()), 'max', int(nenv.max()))
Hb = 0.5 * (H['globcurrent'] + H['glorys12'])       # (84 nodes, 12 items, 212 bins), two models equal weight
mb = ITEMS.index('mossel-bay-engine-cowling-roy')
# ramp prior (period medians 0.1 / 0.5 / 1 / 1; periods: before 29 Jul 2015, to 29 Feb 2016, to 30 Jun 2016, to 30 Jan 2017)
B1, B2, B3 = day('2015-07-29'), day('2016-02-29', True), day('2016-06-30', True)
NU = np.where(DAYS < B1, 0.1, np.where(DAYS < B2, 0.5, 1.0))
def pit_curve(hist, delay):    # discovery-time intensity on a daily grid from a 5-day arrival histogram
    g = np.zeros(len(DAYS))
    for k in np.nonzero(hist > 0)[0]:
        x = DAYS - TC[k]; g += np.where(x > 0, hist[k] * np.exp(-np.maximum(x, 0) / delay) / delay, 0.0)
    return g * NU
def cdf_at(g, t): c = np.cumsum(g); return float(c[int(t)] / c[-1]) if c[-1] > 0 else np.nan
# ---------- 1. Mossel Bay by release latitude
rows = []
for i in range(84):
    h = Hb[i, mb]; tot = h.sum(); cs = np.cumsum(h)
    med = float(TC[np.searchsorted(cs, 0.5 * tot)]) if tot > 0 else np.nan
    g60 = pit_curve(h, 60.0); g9 = pit_curve(h, 60.0 * 10 / 70)
    rows.append(dict(release_lat=LAT[i], core_weight=W[i], kernel_mass_total=tot, kernel_mass_by_day655=float(h[:131].sum()), kernel_mass_by_day745=float(h[:149].sum()),
                     frac_by_day655=float(h[:131].sum() / tot) if tot > 0 else np.nan, frac_by_day745=float(h[:149].sum() / tot) if tot > 0 else np.nan, median_arrival_day=med,
                     a_find_dec2015_delay60=0.5 * (A60['globcurrent'][i, mb] + A60['glorys12'][i, mb]), a_find_dec2015_fresh=0.5 * (A9['globcurrent'][i, mb] + A9['glorys12'][i, mb]),
                     a_find_mar2016_delay60=0.5 * (AM['globcurrent'][i, 0] + AM['glorys12'][i, 0]),
                     pit_find_23Dec2015_delay60=cdf_at(g60, 655.5), pit_find_23Dec2015_fresh=cdf_at(g9, 655.5), pit_find_22Mar2016_delay60=cdf_at(g60, 745.5)))
T1 = pd.DataFrame(rows).sort_values('release_lat'); T1.to_csv('arr-high/tables/mossel-bay-timing-by-release-latitude.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
band = lambda lo, hi: T1[(T1.release_lat >= -hi) & (T1.release_lat < -lo)]
print('\nMossel Bay kernel arrivals by release-latitude band (means over nodes in band; mass in units of particle fraction per km):')
bands = [(36, 40.3), (33, 36), (30, 33), (27, 30), (24, 27), (19.9, 24)]
bt = []
for lo, hi in bands:
    b = band(lo, hi); mass = b.kernel_mass_total.sum(); e = b.kernel_mass_by_day655.sum()
    bt.append(dict(band_S=f'{lo}-{min(hi, 40.25)}', nodes=len(b), core_weight=b.core_weight.sum(), mass_total=mass, mass_by_day655=e, mass_by_day745=b.kernel_mass_by_day745.sum(),
                   frac_by_655=e / mass if mass > 0 else np.nan, frac_by_745=b.kernel_mass_by_day745.sum() / mass if mass > 0 else np.nan,
                   median_arrival_day=float(np.average(b.median_arrival_day, weights=np.maximum(b.kernel_mass_total, 1e-300))),
                   pit_dec_delay60=float(np.average(b.pit_find_23Dec2015_delay60, weights=np.maximum(b.kernel_mass_total, 1e-300))), pit_dec_fresh=float(np.average(b.pit_find_23Dec2015_fresh, weights=np.maximum(b.kernel_mass_total, 1e-300))),
                   pit_mar_delay60=float(np.average(b.pit_find_22Mar2016_delay60, weights=np.maximum(b.kernel_mass_total, 1e-300)))))
BT = pd.DataFrame(bt); BT.to_csv('arr-high/tables/mossel-bay-timing-by-latitude-band.csv', index=False); print(BT.round(4).to_string(index=False))
# ---------- 2. timing PIT of every find, core-weighted source
pr = []
for j, it in enumerate(ITEMS):
    h = (W[:, None] * Hb[:, j, :]).sum(0)
    t = 0.5 * (day(FIND[it]) + day(FIND[it], True))
    r = dict(item=it, find_day=t, find_date=FIND[it], core_mass=float(h.sum()))
    r['pit_delay60'] = cdf_at(pit_curve(h, 60.0), t); r['pit_delay8.6_fresh'] = cdf_at(pit_curve(h, 60.0 * 10 / 70), t)
    # restricted source ranges
    for nm, lo, hi in (('pit_source_36_40S', 36, 40.3), ('pit_source_33_36S', 33, 36), ('pit_source_30_33S', 30, 33), ('pit_source_24_30S', 24, 30)):
        sel = (LAT >= -hi) & (LAT < -lo); hh = Hb[sel, j, :].sum(0); r[nm] = cdf_at(pit_curve(hh, 60.0), t) if hh.sum() > 0 else np.nan
    pr.append(r)
T2 = pd.DataFrame(pr); T2.to_csv('arr-high/tables/timing-pit-by-find.csv', index=False); print('\nTiming PIT (probability that the find date is as early as observed or earlier, given the model):'); print(T2.round(4).to_string(index=False))
# ---------- 4. south-coast (all of S4) arrival time by release latitude band: kernel-free
print('\nAll arrivals on the South Africa south coast segment (class 1, both models), fraction of released particles arriving by day 655 / 745 / 1059:')
SG = 0.5 * (SEG['globcurrent'] + SEG['glorys12'])     # (84, 6, 212)
rows4 = []
for lo, hi in bands:
    sel = (LAT >= -hi) & (LAT < -lo)
    for s_i, nm in ((3, 'S4 south-africa south coast'), (2, 'S3 southern Mozambique'), (0, 'S1 Reunion')):
        h = SG[sel, s_i, :].mean(0); rows4.append(dict(band_S=f'{lo}-{min(hi, 40.25)}', segment=nm, by_day655=float(h[:131].sum()), by_day745=float(h[:149].sum()), by_day1059=float(h.sum())))
T4 = pd.DataFrame(rows4); T4.to_csv('arr-high/tables/coast-segment-arrival-fractions-by-band.csv', index=False); print(T4.round(5).to_string(index=False))
# ---------- 5. dependence on the provisional detection ramp, and predicted find-date quantiles
def curve(hist, delay, flat):
    g = pit_curve(hist, delay); return g / NU if flat else g
def quant(g, p): c = np.cumsum(g) / g.sum(); return float(DAYS[np.searchsorted(c, p)])
rows5 = []
for j, it in enumerate(ITEMS):
    h = (W[:, None] * Hb[:, j, :]).sum(0); t = 0.5 * (day(FIND[it]) + day(FIND[it], True))
    gr, gf = curve(h, 60.0, False), curve(h, 60.0, True)
    rows5.append(dict(item=it, find_day=t, pit_ramp=cdf_at(gr, t), pit_flat_levels=cdf_at(gf, t), pred_find_day_q05_ramp=quant(gr, .05), pred_find_day_q50_ramp=quant(gr, .5), pred_find_day_q95_ramp=quant(gr, .95),
                      pred_find_day_q05_flat=quant(gf, .05), pred_find_day_q50_flat=quant(gf, .5)))
T5 = pd.DataFrame(rows5); T5.to_csv('arr-high/tables/timing-pit-ramp-versus-flat-levels.csv', index=False); print('\nPIT with ramp (provisional) and with equal detection levels in time; predicted find-day quantiles (core-weighted source):'); print(T5.round(3).to_string(index=False))
h = (W[:, None] * Hb[:, mb, :]).sum(0)
print('\nMossel Bay, core-weighted: PIT of 22 Mar 2016 (day 745.5): ramp %.3f, flat %.3f; PIT of 23 Dec 2015 fresh: ramp %.3f, flat %.3f' % (cdf_at(curve(h, 60, False), 745.5), cdf_at(curve(h, 60, True), 745.5), cdf_at(curve(h, 60 * 10 / 70, False), 655.5), cdf_at(curve(h, 60 * 10 / 70, True), 655.5)))
rows6 = []
for lo, hi in bands:
    sel = (LAT >= -hi) & (LAT < -lo); hh = Hb[sel, mb, :].sum(0)
    rows6.append(dict(band_S=f'{lo}-{min(hi, 40.25)}', pit_dec_ramp=cdf_at(curve(hh, 60, False), 655.5), pit_dec_flat=cdf_at(curve(hh, 60, True), 655.5), pit_mar_ramp=cdf_at(curve(hh, 60, False), 745.5), pit_mar_flat=cdf_at(curve(hh, 60, True), 745.5),
                      q05_day_flat=quant(curve(hh, 60, True), .05), q50_day_flat=quant(curve(hh, 60, True), .5)))
T6 = pd.DataFrame(rows6); T6.to_csv('arr-high/tables/mossel-bay-pit-by-band-ramp-versus-flat.csv', index=False); print(T6.round(3).to_string(index=False))
# ---------- 6. all four earliest finds jointly: probability of PIT this low (independent-uniform bound is NOT valid; shown for scale only)
early = T5[T5.item.isin(['reunion-right-flaperon', 'mossel-bay-engine-cowling-roy', 'paindane-right-flap-fairing', 'vilanculos-horizontal-stabilizer-panel'])]
print('\nfour earliest finds, PIT ramp:', early.pit_ramp.round(3).tolist(), 'flat:', early.pit_flat_levels.round(3).tolist(), 'product bound ramp %.2e flat %.2e' % (early.pit_ramp.prod(), early.pit_flat_levels.prod()))
