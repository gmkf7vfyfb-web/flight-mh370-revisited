# exec'd in the analysis kernel (needs MP, getmap, hpd_levels, W, A, seeds, q2m, q2j, q1m, apply_figure_style)
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
from pyproj import Geod
G_ = Geod(ellps='WGS84')
OPT = {0: '00:19 data\nnot used', 1: '00:19:29\nrange only', 2: '00:19:29 range\nand frequency', 3: 'Both 00:19 frequencies\nas recorded',
       4: 'Both 00:19 frequencies,\nshared start-up offset', 5: '00:19:29 frequency as recorded,\n00:19:37 frequency with offset'}
BR = {'T': 'arrival 00:52:03 (text reading)', 'C': 'arrival 00:54:30 (caption reading)'}
FOOT_STE = ('(i) Plain: The data is from the run J flight model (simulated flights after 00:11, end-of-flight descents). We use only flights that '
            'agree with the satellite data. We give each flight a weight for how well its impact time and place agree with the sound that Kadri (2024) '
            'found at the H01W hydrophone on bearing 306.18 deg. Shaded areas contain 50 %, 90 % and 99 % of the weighted impacts. The sample near the bearing is small, '
            'thus the areas are not stable. Haixun 01 is a secondary check only. Searches, drift and other evidence are not used.')
FOOT_TECH = ('(ii) Technical: source posterior end-of-flight run J (strata waypoints/free/repro-radar/descent-climb, P(family) 0.9982/0.0013/0.0003/0.0002, 74 seeds), '
             'cells "D{d} total q=0.333 (C2 silent)" (log-on cause mixture p(C1) = 0.75, survival factor applied); physics PROVISIONAL (interim pitch-down, '
             'piloted turns, residual roll P(left) 0.8, round-3 free-flight laws); acoustic likelihood per pre-registration Q2 (c = 1.48 km/s, '
             's_t^2 = (d 0.015/1.48^2)^2 + 25 s^2, s_b = %s deg); grid 0.05 deg; HPD 50/90/99 %%; search case: none; ocean model: none; exclusions: none; '
             'Kish ESS < 1,000 in every panel, so every panel is NOT ESTIMABLE (end-of-flight map threshold).')


def arc_line():
    lats = np.linspace(-30, -20, 201); out = []
    for la in lats:
        lo = np.linspace(95, 106, 2201); b = bto_sl(np.full_like(lo, la), lo) - 18400.0
        i = np.nonzero(np.diff(np.sign(b)))[0]
        if len(i): j = i[0]; out.append((la, lo[j] - b[j] * (lo[j + 1] - lo[j]) / (b[j + 1] - b[j])))
    return np.array(out)


def bearing_line(az=W.AZ, r0=1400, r1=1950):
    s = np.linspace(r0, r1, 60) * 1e3; lo, la, _ = G_.fwd(np.full(60, W.H01[1]), np.full(60, W.H01[0]), np.full(60, az), s); return la, lo


def map_panel(ax, H, ess, title, ext):
    latc = W.LOC['lat0'] + (np.arange(H.shape[0]) + 0.5) * W.LOC['step']; lonc = W.LOC['lon0'] + (np.arange(H.shape[1]) + 0.5) * W.LOC['step']
    l50, l90, l99 = hpd_levels(H)
    Z = np.zeros_like(H); Z[H >= l99] = 1; Z[H >= l90] = 2; Z[H >= l50] = 3
    cm = mpl.colors.ListedColormap(['white', '#d9d9d9', '#969696', '#252525'])
    ax.pcolormesh(lonc, latc, Z, cmap=cm, vmin=-0.5, vmax=3.5, shading='nearest', rasterized=True)
    al = ARC; ax.plot(al[:, 1], al[:, 0], color='#1f78b4', lw=0.9)
    la, lo = bearing_line(); ax.plot(lo, la, color='#e66101', lw=0.9, ls='--')
    ax.plot(W.XC[1], W.XC[0], marker='o', ms=4, mfc='#e66101', mec='k', mew=0.4, ls='none')
    ax.plot(W.HX[1], W.HX[0], marker='^', ms=4, mfc='none', mec='k', mew=0.6, ls='none')
    ax.set_xlim(ext[2], ext[3]); ax.set_ylim(ext[0], ext[1]); ax.set_aspect(1 / np.cos(np.radians(-25.7)))
    ax.set_title(title, loc='left')
    ax.text(0.02, 0.03, f'NOT ESTIMABLE\neffective sample {ess:.0f}', transform=ax.transAxes, fontsize=6, va='bottom',
            bbox=dict(fc='white', ec='none', alpha=0.8, pad=1))


def fig_maps(sb='1.0', opts=(0, 2, 4, 3), fn='fig-conditional-impact-maps'):
    ext = (-28.0, -23.0, 99.0, 104.0)
    fig, axs = plt.subplots(2, len(opts), figsize=(7.2, 4.9), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.06, hspace=0.25))
    for i, b in enumerate('TC'):
        for j, d in enumerate(opts):
            k = f'D{d} total q=0.333 (C2 silent)'; H, _ = getmap('main', k, f'{b}{sb}')
            ess = float(q2m[(q2m.key == k) & (q2m.variant == f'{b}{sb}')].ess_conditional.iloc[0])
            map_panel(axs[i, j], H, ess, OPT[d] if i == 0 else '', ext); axs[i, j].set_xticks([100, 101, 102, 103])
            if j == 0: axs[i, j].set_ylabel(f'Given {BR[b]}\nlatitude (deg)')
            if i == 1: axs[i, j].set_xlabel('longitude (deg)')
    h = [mpl.patches.Patch(fc='#252525', label='50 %'), mpl.patches.Patch(fc='#969696', label='90 %'), mpl.patches.Patch(fc='#d9d9d9', ec='0.6', lw=0.3, label='99 %'),
         mpl.lines.Line2D([], [], color='#1f78b4', lw=0.9, label='7th arc, sea level'), mpl.lines.Line2D([], [], color='#e66101', ls='--', lw=0.9, label='H01W bearing 306.18 deg'),
         mpl.lines.Line2D([], [], marker='o', mfc='#e66101', mec='k', ls='none', ms=4, label='bearing on the arc'),
         mpl.lines.Line2D([], [], marker='^', mfc='none', mec='k', ls='none', ms=4, label='Haixun 01 contact (check only)')]
    fig.legend(handles=h, loc='upper center', ncol=7, frameon=False, fontsize=6, bbox_to_anchor=(0.5, 0.995), handlelength=1.2, columnspacing=0.8)
    fig.suptitle('Impact area given the H01W sound, highest-density regions', y=1.035, x=0.06, ha='left')
    fig.text(0.06, -0.035, FOOT_STE, fontsize=5.5, wrap=True, va='top')
    fig.text(0.06, -0.115, FOOT_TECH % sb, fontsize=5.5, wrap=True, va='top')
    fig.savefig(f'kh/fig/{fn}-sb{sb}.png', dpi=300, bbox_inches='tight'); fig.savefig(f'kh/fig/{fn}-sb{sb}.pdf', bbox_inches='tight'); plt.close(fig)


def fig_bf(fn='fig-bayes-factors'):
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ds = list(range(6)); xo = {'T1.0': -0.21, 'T0.5': -0.07, 'C1.0': 0.07, 'C0.5': 0.21}
    col = {'T': '#e66101', 'C': '#5e3c99'}; mk = {'1.0': 'o', '0.5': 's'}
    for vn, dx in xo.items():
        sub = q2m[q2m.key.str.contains('total') & (q2m.variant == vn)].copy(); sub['d'] = sub.key.str[1].astype(int)
        x = sub.d + dx
        ax.vlines(x, sub.seed_lnB_min, sub.seed_lnB_max, color=col[vn[0]], lw=0.6, alpha=0.5)
        ax.plot(x, sub.ln_B_rate, marker=mk[vn[1:]], ls='none', color=col[vn[0]], mfc=col[vn[0]] if vn.endswith('1.0') else 'white', ms=4,
                label=f"{BR[vn[0]]}, bearing sigma {vn[1:]} deg")
    sub = q2j[q2j.variant == 'T1.0']; ax.plot(sub.key.str[1].astype(int) - 0.21, sub.ln_B_rate, marker='x', ls='none', color='0.3', ms=4, label='planned descent before 00:11 (arm V2), 00:52:03, 1.0 deg')
    sub = q2j[q2j.variant == 'C1.0']; ax.plot(sub.key.str[1].astype(int) + 0.07, sub.ln_B_rate, marker='+', ls='none', color='0.3', ms=5, label='planned descent before 00:11 (arm V2), 00:54:30, 1.0 deg')
    ax.axhline(0, color='0.5', lw=0.6)
    ax.set_xticks(ds); ax.set_xticklabels(['00:19 data\nnot used','00:19:29\nrange only','00:19:29 range\nand frequency','Both 00:19\nfrequencies\nas recorded','Both 00:19\nfrequencies, shared\nstart-up offset','00:19:29 frequency\nas recorded, 00:19:37\nwith offset'], fontsize=6); ax.set_ylabel('ln Bayes factor\n(impact sound vs chance transient)')
    ax.set_title('ln Bayes factor is below 0 under every 00:19 treatment and both arrival readings', loc='left')
    ax.legend(frameon=False, fontsize=6, loc='lower left', ncol=2); ax.set_ylim(-16, 2); ax.margins(x=0.04)
    fig.text(0.0, -0.17, ('(i) Plain: Values below 0 mean the satellite-based flight model makes the H01W sound less likely as the impact than as one of the '
                          'other sounds in the same 21 minutes. Bars show the range over the 24 main-route seeds; long bars mean the value is not stable. '
                          'Searches, drift and other evidence are not used.'), fontsize=5.5, wrap=True, va='top')
    fig.text(0.0, -0.26, ('(ii) Technical: ln B = ln( sum_i w_i L_i / lambda ), lambda = 18/(1,260 s x 140 deg) (Kadri Table 1 rate over 00:36-00:57 and 200-340 deg); '
                          'w_i = end-of-flight run J cells "D{d} total q=0.333 (C2 silent)" mixed over four strata; arm V2 = run-j-joined-v2 seeds 1-21 (D0-D4). '
                          'Sensitivity: one chance arrival without the 18-transient rate adds ln 18 = +2.89 to every value. Bars: per-seed min-max over run-j-waypoints seeds. Conditional effective samples 1-280: every value UNCONVERGED (estimability rule: '
                          '>= 30 effective parents per seed not met). Physics PROVISIONAL; no search, drift or hydro-propagation terms.'), fontsize=5.5, wrap=True, va='top')
    fig.savefig(f'kh/fig/{fn}.png', dpi=300, bbox_inches='tight'); fig.savefig(f'kh/fig/{fn}.pdf', bbox_inches='tight'); plt.close(fig)
