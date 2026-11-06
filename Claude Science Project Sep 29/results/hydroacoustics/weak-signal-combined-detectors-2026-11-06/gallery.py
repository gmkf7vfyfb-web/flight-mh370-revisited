"""Annotated spectrogram gallery: injected signals, real weak earthquakes, strongest background false alarms."""
import sys, os, glob, json, textwrap, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import genpareto
from obspy import UTCDateTime
import sigdet as SD, sigcorr as SC, pmap, inject as I
from score_records import load

B = pd.read_csv('joint_background.csv'); PM = pmap.PMap(B, 'rnd'); CN = np.load('corr_norm.npz')
STN = {'H01W': 'Cape Leeuwin', 'H08S': 'Diego Garcia South'}
COL = {'L_d0': '#7f7f7f', 'L_d1': '#1f77b4', 'S_d1': '#d62728', 'C_any': '#9467bd', 'C_imp': '#ff7f0e', 'E_pers': '#2ca02c', 'COMB': 'k'}
LEVELS = [(0.5, '50% per look'), (0.2, '20% per look'), (0.05, '5% per look'), (0.05 / 15, '5% per 30 min'), (1 / 720, '1 per day')]
RB = '/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'


def pcomb(st, F):
    Fs = PM.f[(st, 'COMB')]; n = len(Fs); m = int(0.1 * n); u = Fs[-m - 1]
    c, _, sc = genpareto.fit(Fs[-m:] - u + 1e-9, floc=0)
    F = np.asarray(F, float)
    pe = (n - np.searchsorted(Fs, F, side='left') + 1) / (n + 1)
    return np.clip(np.where(F > u, 0.1 * genpareto.sf(F - u, c, 0, sc), pe), 1e-15, 1)


def traces(y, xref, st, Nref=None):
    """All detector traces on a 5 s grid; returns t_spec, Ydb, grid, dict of -log10 p."""
    t, P = SD.spec(y)
    N = SD.noise_psd(SD.spec(xref)[1]) if Nref is None else Nref
    N = np.maximum(N, 1e-30)
    Y = P[SD.FB] / N[SD.FB]; Nf = np.median(N[SD.FB], 1)
    banks = SD.bank_spectral(Nf); envs = SD.bank_envelopes(); out = {}
    for shape, key in ((False, 'L'), (True, 'S')):
        S = SD.d1_scores(Y, banks, envs, SD.PAIRS, shape=shape); S['whale'] = SD.d1_whale(Y, I.WT, shape=shape)
        S['d0'] = SD.d0_band_energy(P, N); out[key] = SD.combine(S)
    c = np.arange(330.0, len(y) / SD.FS - 330.0, 5.0)
    As = SC.local_whiteners(xref, c); za, zi = SC.corr_stats(SC.lags_with(y, c, As), CN[st + '_mu'], CN[st + '_sd'], SC.record_bank(xref))
    pe = SC.persistence(SC.envelope_db(y), c, SC.TAU[st])
    raw = {'L_d0': out['L']['d0'], 'L_d1': out['L']['d1'], 'S_d1': out['S']['d1']}
    g = {}
    for k, v in raw.items():   # spectral traces: max within +-2.5 s of each grid point
        g[k] = np.array([np.nanmax(v[(t >= cc - 2.5) & (t < cc + 2.5)]) for cc in c])
    g['C_any'], g['C_imp'], g['E_pers'] = za, zi, pe
    lp = {k: -np.log10(PM.p(st, k, v)) for k, v in g.items()}
    F = PM.fisher(st, {k: g[k] for k in pmap.COMB}); lp['COMB'] = -np.log10(pcomb(st, F))
    return t, 10 * np.log10(np.maximum(Y, 1e-3)), SD.F[SD.FB], c, lp


SHORT = {'COMB': 'Combined', 'L_d0': 'Band energy', 'L_d1': 'Impact spectral templates', 'S_d1': 'Spectral shape change',
         'C_any': 'Correlation, no template', 'C_imp': 'Correlation, impact pattern', 'E_pers': 'Envelope persistence'}


def panel(fig, gs, t, Ydb, f, c, lp, t0, title, st, note='', look=(-40, 80), xl=(-180, 300)):
    a1 = fig.add_subplot(gs[0, 0]); a2 = fig.add_subplot(gs[1, 0], sharex=a1)
    cax = fig.add_subplot(gs[0, 1]); side = fig.add_subplot(gs[:, 2]); side.axis('off')
    tr = t - t0
    m = (tr >= xl[0] - 5) & (tr <= xl[1] + 5)
    im = a1.pcolormesh(tr[m], f, Ydb[:, m], vmin=-3, vmax=12, cmap='magma', shading='auto', rasterized=True)
    a1.set_ylabel('Frequency (Hz)'); a1.set_ylim(3, 60); plt.setp(a1.get_xticklabels(), visible=False)
    for a in (a1, a2):
        a.axvspan(*look, color='#4a90d9', alpha=0.15, lw=0); a.axvline(0, color='#7fb3ff', lw=0.8, ls='--')
    a1.set_title(title, loc='left')
    cb = fig.colorbar(im, cax=cax); cb.set_label('dB above local noise')
    cr = c - t0; mm = (cr >= xl[0]) & (cr <= xl[1])
    for k in pmap.STATS + ['COMB']:
        a2.plot(cr[mm], np.minimum(lp[k][mm], 6.2), color=COL[k], lw=1.6 if k == 'COMB' else 0.9, label=SHORT[k], zorder=3 if k == 'COMB' else 2)
    for p, lab in LEVELS:
        a2.axhline(-np.log10(p), color='#999999', lw=0.5, ls=':'); a2.text(xl[1] + 4, -np.log10(p), lab, va='center', color='#555555', fontsize=5)
    a2.set_ylim(0, 6.3); a2.set_xlim(*xl)
    a2.set_ylabel('Background chance\n(-log10, per 2 min look)'); a2.set_xlabel('Time from added signal start or predicted arrival (s)')
    lw = (cr >= look[0]) & (cr <= look[1]); txt = []
    for k in ['COMB'] + pmap.STATS:
        v = np.nanmax(lp[k][lw]) if lw.any() else np.nan
        txt.append(f"{SHORT[k]:27s}{10 ** -v:8.2g}")
    h, l = a2.get_legend_handles_labels()
    side.legend(h, l, loc='upper left', frameon=False, fontsize=5.5, bbox_to_anchor=(0.2, 1.0))
    side.text(0.2, 0.42, 'Lowest background chance\nin the shaded look window\n\n' + '\n'.join(txt) + ('\n\n' + note if note else ''),
              transform=side.transAxes, fontsize=5.2, va='top', family='monospace')
    return a2


def injection_case(st, cls, seed, snr):
    """Rebuild one injection case exactly as inject.case does (same rng order)."""
    rng = np.random.default_rng(seed)
    recs = sorted(os.path.basename(p)[:-6] for p in glob.glob(f'{RB}/{st}1_rnd*.mseed'))
    for _ in range(50):
        k = recs[rng.integers(len(recs))]
        t0, x = load(f'{RB}/{k}.mseed', st); T = len(x) / SD.FS
        tc = rng.uniform(I.SEG / 2 + 5, T - I.SEG / 2 - 5)
        i0 = int((tc - I.SEG / 2) * SD.FS); seg = x[i0: i0 + int(I.SEG * SD.FS)]
        if (seg == 0).mean() > 0.001:
            continue
        break
    t, P = SD.spec(seg); N = SD.noise_psd(P); jc = np.argmin(abs(t - I.SEG / 2))
    nb = (N[SD.FB0, jc] * (SD.F[1] - SD.F[0])).sum()
    if cls == 'realquake':
        s, src = I.real_signal(st, rng); tsig0 = 30.0
    else:
        s, tsig0 = SD.synth(cls, rng); s = SC.instrument(s)
    j0 = int((I.SEG / 2 - tsig0) * SD.FS)
    full = np.zeros_like(seg); L = min(len(s), len(seg) - j0); full[j0: j0 + L] = s[:L]
    xf = x.copy(); xf[i0: i0 + len(seg)] += SD.band_snr_scale(full, nb, snr)
    return x, xf, tc, k


FOOT = ("Open IMS hydrophone data (EarthScope), element 1, 250 samples/s. Spectrogram: 1 s Hann frames, whitened by a 10 min running median noise spectrum. "
        "Lower panel: for each detector, the chance that real background alone gives this score or higher in a 2 min look (144 / 178 random 40 min records, "
        "2015-2025, generalised Pareto tail beyond the 90th percentile). Combined = Fisher sum of band energy, spectral shape change, correlation with the impact "
        "pattern and envelope persistence, calibrated on the same background. Shaded: the 2 min look window used for scoring. SNR = largest 30 s signal energy "
        "in 5-40 Hz over the local noise energy in 30 s. Synthetic signals: 1,500-4,500 km deep channel, 2-4 Hz low cut-off, Thorp absorption, 1-95 Hz instrument "
        "response. Spectral-template scores are tied to the template start, so they rise up to about 90 s before a signal. Provisional methods test; no 8 March 2014 data used.")


def page(pdf, items, fname=None):
    plt.rcParams.update({'font.size': 7, 'axes.titlesize': 7.5, 'axes.labelsize': 7, 'xtick.labelsize': 6, 'ytick.labelsize': 6})
    fig = plt.figure(figsize=(8.27, 11.0))
    outer = fig.add_gridspec(len(items), 1, hspace=0.28, top=0.97, bottom=0.1, left=0.09, right=0.99)
    for i, it in enumerate(items):
        gs = outer[i].subgridspec(2, 3, height_ratios=[1.1, 1], width_ratios=[1, 0.025, 0.42], hspace=0.06, wspace=0.03)
        panel(fig, gs, *it['tr'], it['t0'], it['title'], it['st'], note=it.get('note', ''))
    fig.text(0.04, 0.012, '\n'.join(textwrap.wrap(FOOT, 190)), fontsize=5.2)
    pdf.savefig(fig, dpi=200)
    if fname:
        fig.savefig(fname, dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    inj = pd.read_csv('injections_rnd_v3.csv')
    ex = []
    NAMEC = {'dive': 'High-energy dive', 'ditch': 'Prolonged shallow ditching', 'realquake': 'Real earthquake sound, scaled down',
             'zcall': 'Blue whale Z-call', 'airgun': 'Airgun shot train', 'implosion': 'Implosion'}
    plan = [('dive', [-10, -5, 0, 5]), ('ditch', [-10, -5, 0, 5]), ('realquake', [-5, 0]), ('zcall', [-5]), ('airgun', [0]), ('implosion', [-5])]
    for st in ('H01W', 'H08S'):
        for cls, snrs in plan:
            seed = int(inj[(inj.st == st) & (inj.cls == cls)].seed.min())
            for snr in snrs:
                x0, y, tc, k = injection_case(st, cls, seed, snr)
                tr = traces(y, x0, st)
                row = inj[(inj.st == st) & (inj.cls == cls) & (inj.seed == seed) & (inj.snr == snr)]
                ex.append(dict(st=st, tr=tr, t0=tc, kind='inj',
                               title=f'{NAMEC[cls]} added at {snr:+.0f} dB to real noise, {STN[st]}', note=f'Case {seed}; host record {k}',
                               check=dict(L_d0=float(row.L_d0.iloc[0]) if len(row) else None)))
                print('inj', st, cls, snr, flush=True)
    # real weak catalogued earthquakes at predicted times
    kc = pd.read_csv('known_events_control.csv'); RD = '/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_eq_records'
    rng = np.random.default_rng(5)
    for st in ('H01W', 'H08S'):
        w = kc[(kc.st == st) & (kc.snr_db < 12)].sample(3, random_state=5)
        for _, r in w.iterrows():
            t0, x = load(f'{RD}/{r.rec}.mseed', st)
            ev = pd.read_csv(f'bc/out/eq_{st}_events.csv').set_index('evid').loc[r.evid]
            tp = UTCDateTime(ev.t_pred) - t0
            tr = traces(x, x, st)
            ex.append(dict(st=st, tr=tr, t0=tp, kind='eq', title=f'Real weak earthquake at its predicted arrival, {STN[st]}: magnitude {ev.mag}, {ev.dist_km:.0f} km', note=f'Catalogue event {r.evid}\nearlier measured SNR {r.snr_db:.1f} dB\n{str(UTCDateTime(ev.t_pred))[:19]} UTC'))
            print('eq', st, r.evid, flush=True)
    # strongest combined-detector looks in the random background (what fools the detectors)
    Bs = B[B.kind == 'rnd'].copy()
    for st in ('H01W', 'H08S'):
        m = Bs.st == st; Bs.loc[m, 'F'] = PM.fisher(st, {s: Bs.loc[m, s].values for s in pmap.COMB})
        top = Bs[m].sort_values('F', ascending=False).drop_duplicates('rec').head(3)
        for _, r in top.iterrows():
            t0, x = load(f'{RB}/{r.rec}.mseed', st)
            tr = traces(x, x, st)
            lp = tr[4]['COMB']; c = tr[3]; mm = (c >= r.b0) & (c < r.b0 + 120); tpk = c[mm][np.argmax(lp[mm])]
            ex.append(dict(st=st, tr=tr, t0=tpk - 20, kind='bg', title=f'One of the strongest background false alarms, {STN[st]} (nothing added)', note=f'{str(t0 + tpk)[:19]} UTC\nrecord {r.rec}'))
            print('bg', st, r.rec, flush=True)
    with PdfPages('spectral-detection-gallery.pdf') as pdf:
        for i in range(0, len(ex), 2):
            page(pdf, ex[i:i + 2], fname=f'gallery_p{i // 2 + 1:02d}.png')
    print('pages', (len(ex) + 1) // 2)
