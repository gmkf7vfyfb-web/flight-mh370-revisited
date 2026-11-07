"""Figures for the 7 Nov 2026 drift convergence and coefficient run. Working version (colour, footnotes) and Journal of
Navigation version (greyscale, no title, no footnotes, 127 mm wide, caption separate).
Usage: python conv_figures.py <analysis_dir> <accumulators.npz> <out_dir>"""
import sys, os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt
RES, ACC, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
NV = pd.read_csv(f'{RES}/node-values-all-cases.csv'); lat = NV['lat'].values; lon = NV['lon'].values
A = np.load(ACC); H = A['H_D0_all'].astype(float); hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
hlat = hl0 + (np.arange(H.shape[0]) + .5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + .5) * hg; ii, jj = np.nonzero(H > 0)
cl, cn, hw = hlat[ii], hlon[jj], H[ii, jj]
dist = np.hypot((cn[:, None] - lon[None]) * 111.2 * np.cos(np.radians(cl[:, None])), (cl[:, None] - lat[None]) * 111.2)
nn = np.argsort(dist, 1)[:, :6]; W = 1 / np.maximum(np.take_along_axis(dist, nn, 1), 1.) ** 2; W /= W.sum(1, keepdims=True); p0 = hw / hw.sum()
def post(case):
    a = (W * NV[f'globcurrent|{case}'].values[nn]).sum(1); b = (W * NV[f'glorys12|{case}'].values[nn]).sum(1); mx = max(a.max(), b.max())
    p = p0 * 0.5 * (np.exp(a - mx) + np.exp(b - mx)); return p / p.sum()
def mean_shift(case): return (post(case) * cl).sum() - (p0 * cl).sum()
bins = np.arange(-41.0, -19.75, 0.25); mid = 0.5 * (bins[1:] + bins[:-1])
def dens(p): return np.histogram(cl, bins, weights=p)[0] / 0.25
NAMES = {'reunion-right-flaperon': 'Flaperon, Réunion (Jul 2015)', 'mossel-bay-engine-cowling-roy': 'Engine cowling, Mossel Bay (Dec 2015)',
         'paindane-right-flap-fairing': 'Flap fairing, Paindane (Dec 2015)', 'vilanculos-horizontal-stabilizer-panel': 'Stabiliser panel, Vilanculos (Feb 2016)',
         'rodrigues-door-closet-panel': 'Closet door panel, Rodrigues (Mar 2016)', 'chidenguele-right-fan-cowling': 'Fan cowling, Chidenguele (Apr 2016)',
         'mauritius-left-outboard-flap': 'Outboard flap, Mauritius (May 2016)', 'antsiraka-cabin-interior-panel': 'Cabin panel, Antsiraka (Jun 2016)',
         'pemba-right-outboard-flap': 'Outboard flap, Pemba (Jun 2016)'}
RATIOS = [0.05, 0.1, 0.25, 0.5, 0.65, 1.0]
base_mean = (p0 * cl).sum(); fo = mean_shift('finds only')
tab = dict(core_mean=base_mean, finds_only=fo,
           tier={r: mean_shift(f'Australia ratio {r}') for r in RATIOS}, pop={r: mean_shift(f'Australia ratio {r}, populated only') for r in RATIOS},
           tier_h={r: (mean_shift(f'Australia ratio {r} half a'), mean_shift(f'Australia ratio {r} half b')) for r in RATIOS},
           only={k: mean_shift(f'only {k}') for k in NAMES}, allbut={k: mean_shift(f'all but {k}') for k in NAMES})

FOOT_STE = ("Simple summary: The curves show where the aircraft entered the sea, along the 7th arc. The satellite and flight data give the black curve. "
            "The debris finds move it a little north. One engine cowling found at Mossel Bay causes almost all of that move. "
            "The flaperon alone does not move it. No debris was found in Australia. That moves the curve further north, by an amount that depends on how likely "
            "people on Australian beaches were to find and report debris, compared with the African and island coasts.")
FOOT_TECH = ("Technical: run J impact samples, end-of-flight families pooled, 00:19 data held out; drift likelihood ln L = ln mean over ocean environments (32 south of 33.25 S, 16 north) x 256 detection-level draws "
             "of sum over finds of [ln(a.nu) - ln(A.nu)]; 84 release points 20-40 S on the run J median track and +/-50 NM; 6,250 particles per class per environment; "
             "GLORYS12 and GlobCurrent (product-relative windage) with ERA5 wind, equal weight in likelihood; 50 km find kernel; nine confirmed or almost-certain finds; "
             "Australian tiers city+inner = ratio, outer regional = 0.3 x ratio, remote = 0 (17 Oct ruling, ratio is a sensitivity); provisional windage, delay and level priors; "
             "no Bayes factor implied; coefficient jobs 91ee26ce and 272016f7, offline scorer validated against the module to 1.3e-6.")
def draw(fig, axs, grey):
    k = '0.0' if grey else None
    C = dict(core='black', finds='#1f77b4', flap='#2ca02c', r25='#d62728', r1='#9467bd') if not grey else dict(core='black', finds='0.35', flap='0.55', r25='0.2', r1='0.6')
    ax = axs[0]
    for case, lab, sty, col, lw in [(None, 'Satellite and flight data alone', '-', C['core'], 1.6), ('only reunion-right-flaperon', 'With the flaperon alone', (0, (1, 1.2)), C['flap'], 1.4),
                                    ('finds only', 'With all nine finds', '--', C['finds'], 1.3), ('Australia ratio 0.25', 'Nine finds and no Australian finds, ratio 0.25', '-.', C['r25'], 1.3),
                                    ('Australia ratio 1.0', 'Nine finds and no Australian finds, ratio 1', (0, (5, 1.5, 1, 1.5, 1, 1.5)), C['r1'], 1.3)]:
        p = p0 if case is None else post(case); ax.plot(mid, dens(p), ls=sty, color=col, lw=lw, label=lab)
    ax.set_xlim(-40.5, -26); ax.set_ylim(bottom=0); ax.set_xlabel('Latitude on the 7th arc (deg, negative = south)'); ax.set_ylabel('Probability density (per deg)')
    ax.legend(frameon=False, loc='upper right', fontsize=6.5, handlelength=3.2)
    if not grey: ax.set_title('Debris evidence moves the impact distribution north, mainly through the Australian non-finds', loc='left', fontsize=8)
    ax = axs[1]
    x = np.array(RATIOS); y = np.array([tab['tier'][r] for r in RATIOS]); yp = np.array([tab['pop'][r] for r in RATIOS])
    ax.plot(x, y, '-o', color='black' if grey else C['r25'], ms=4, lw=1.2, label='Populated and outer regional coasts')
    ax.plot(x, yp, '--s', color='0.45' if grey else C['r1'], mfc='white', ms=4, lw=1.2, label='Populated coasts only')
    for r in RATIOS:
        a, b = tab['tier_h'][r]; ax.plot([r, r], [a, b], color='0.3', lw=2.5, alpha=0.6, solid_capstyle='butt')
    ax.axhline(fo, color='0.4', ls=':', lw=1); ax.text(0.06, fo - 0.12, f'All nine finds, no Australian term: +{fo:.2f} deg', fontsize=6.5, color='0.25', va='top')
    ax.set_xscale('log'); ax.set_xticks(RATIOS); ax.set_xticklabels(['0.05', '0.1', '0.25', '0.5', '0.65', '1']); ax.minorticks_off()
    ax.set_xlabel('Australian detection ratio (relative to the coasts where debris was found)'); ax.set_ylabel('Shift of mean latitude (deg north)')
    ax.set_ylim(0, max(y.max(), yp.max()) * 1.18); ax.legend(frameon=False, loc='upper left', fontsize=6.5)
    if not grey: ax.set_title('Even a low Australian detection ratio adds a northward shift', loc='left', fontsize=8)
    ax = axs[2]
    keys = sorted(NAMES, key=lambda k: tab['only'][k]); yy = np.arange(len(keys))
    ax.axvline(0, color='0.6', lw=0.8); ax.axvline(fo, color='0.4', ls=':', lw=1)
    ax.plot([tab['only'][k] for k in keys], yy, 'o', color='black', ms=4.5, label='This find alone')
    ax.plot([tab['allbut'][k] for k in keys], yy, 'D', mfc='white', mec='0.35', ms=4.5, label='All finds except this one')
    ax.set_yticks(yy); ax.set_yticklabels([NAMES[k] for k in keys], fontsize=6.5); ax.set_xlabel('Shift of mean latitude (deg north)')
    ax.text(fo, -0.95, ' all nine finds', fontsize=6.5, color='0.25', va='bottom'); ax.set_ylim(-1.0, len(keys) - 0.4)
    ax.legend(frameon=False, loc='lower left', bbox_to_anchor=(0.0, 1.0), ncol=2, fontsize=6.5, borderaxespad=0.2)
    if not grey: ax.set_title('One find, the Mossel Bay engine cowling, carries the finds-only shift', loc='left', fontsize=8, pad=16)
    for a, l in zip(axs, 'abc'):
        pos = a.get_position(); fig.text(0.01, pos.y1 + (0.03 if l == 'c' else 0.006), f'({l})', fontsize=8, fontweight='bold', ha='left', va='bottom')
def make(grey):
    w = 127 / 25.4 if grey else 180 / 25.4; h = 7.6 if grey else 11.6
    fig = plt.figure(figsize=(w, h))
    top = 0.97; bot = 0.07 if grey else 0.27
    gs = fig.add_gridspec(3, 1, left=0.43 if grey else 0.30, right=0.97, top=top, bottom=bot, hspace=0.42, height_ratios=[1.1, 1, 1.15])
    axs = [fig.add_subplot(gs[i]) for i in range(3)]
    for a in axs[:2]:  # widen the two upper panels to the left
        pos = a.get_position(); a.set_position([0.12 if grey else 0.09, pos.y0, pos.x1 - (0.12 if grey else 0.09), pos.height])
    draw(fig, axs, grey)
    if not grey:
        import textwrap
        fig.text(0.02, 0.19, '\n'.join(textwrap.wrap(FOOT_STE, 150)), fontsize=6, va='top')
        fig.text(0.02, 0.115, '\n'.join(textwrap.wrap(FOOT_TECH, 170)), fontsize=5.4, va='top', color='0.25')
    return fig
for grey in (False, True):
    plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans'})
    fig = make(grey); stem = f'{OUT}/drift-evidence-on-impact-latitude' + ('-jon' if grey else '')
    if grey:
        fig.savefig(stem + '-word.png', dpi=600); fig.savefig(stem + '.pdf')
    else:
        fig.savefig(stem + '.png', dpi=200); fig.savefig(stem + '.pdf')
    plt.close(fig)
CAP = ("Figure X. Effect of the recovered-debris evidence on the distribution of the impact position along the 7th arc. "
       "(a) Probability density of impact latitude from the satellite and flight data alone, and with the drift likelihood of the flaperon alone, of all nine "
       "confirmed or almost-certain finds, and of the nine finds together with the absence of finds on Australian coasts at detection ratios 0.25 and 1. "
       "(b) Shift of the mean impact latitude against the Australian detection ratio, relative to the coasts where debris was found; grey bars join the two "
       "independent particle halves. (c) Shift produced by each find alone and by all finds except that one. Drift likelihood from forward simulation in two "
       "ocean reanalyses (equal weight), with 32 ocean-environment realisations per release point south of 33.25 S and 16 north of it; the 00:19 satellite data are not used.")
open(f'{OUT}/drift-evidence-on-impact-latitude-jon-caption.txt', 'w').write(CAP + '\n')
# proof: JON image with the caption beneath
import textwrap
img = plt.imread(f'{OUT}/drift-evidence-on-impact-latitude-jon-word.png'); hh, ww = img.shape[:2]
fig = plt.figure(figsize=(127 / 25.4, 127 / 25.4 * hh / ww + 1.3)); ax = fig.add_axes([0, 1.3 / (127 / 25.4 * hh / ww + 1.3), 1, 1 - 1.3 / (127 / 25.4 * hh / ww + 1.3)]); ax.imshow(img); ax.axis('off')
fig.text(0.02, 1.25 / (127 / 25.4 * hh / ww + 1.3), '\n'.join(textwrap.wrap(CAP, 118)), fontsize=6.3, va='top'); fig.savefig(f'{OUT}/drift-evidence-on-impact-latitude-jon-proof.pdf'); plt.close(fig)
pd.DataFrame(dict(case=['core mean latitude', 'finds only'] + [f'Australia ratio {r}' for r in RATIOS] + [f'Australia ratio {r}, populated only' for r in RATIOS]
                  + [f'only {k}' for k in NAMES] + [f'all but {k}' for k in NAMES],
                  value=[tab['core_mean'], fo] + [tab['tier'][r] for r in RATIOS] + [tab['pop'][r] for r in RATIOS] + [tab['only'][k] for k in NAMES] + [tab['allbut'][k] for k in NAMES])
             ).to_csv(f'{OUT}/figure-values.csv', index=False)
print('ok', round(fo, 3), {r: round(v, 3) for r, v in tab['tier'].items()})
