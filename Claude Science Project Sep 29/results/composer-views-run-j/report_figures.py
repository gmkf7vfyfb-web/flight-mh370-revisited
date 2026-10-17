"""Composer views on run J, step 3b: figures. Run inside the session kernel after apply_figure_style() (figure-style skill);
standalone it falls back to matplotlib defaults. Usage: exec with OUT set, or python report_figures.py OUTDIR"""
import sys, json, pathlib, importlib.util, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = pathlib.Path(__file__).resolve().parent if '__file__' in globals() else pathlib.Path(HERE_DIR)
sys.path.insert(0, str(HERE)); PROJ = HERE.parents[1]
import views_common as V
OUT = pathlib.Path(sys.argv[1]) if 'OUT' not in globals() else pathlib.Path(OUT)
RJ = json.load(open(OUT / 'views-run-j.json')); VI = np.load(OUT / 'view-a-i.npz')
try:
    apply_figure_style(sizes=(8, 7, 6))
except NameError:
    pass
BE = np.arange(-50, -5, 1.0); BM = BE[:-1] + 0.5
C0 = RJ['cells']['head|D0|mix']; B0 = RJ['boot']['D0']
DN = {'D0': '00:19 data\nheld out', 'D1': '00:19:29\nBTO', 'D2': '00:19:29\nBTO + BFO', 'D3': 'both BFOs\nas recorded', 'D4': 'both BFOs,\nshared offset', 'D5': '00:19:37 BFO\nwith offset'}
GREY = '#9a9a9a'; BLACK = '#202020'
COL = {'D': '#1f5fa8', 'S': '#b8641a', 'P': '#7a3d8f', 'A': '#b0283c'}
def vi_bands(E):
    lat, m = VI['mids'], VI[E]; return np.array([m[(lat >= a) & (lat < a + 1)].sum() for a in BE[:-1]]) / m.sum()
def step(ax, y, **kw):
    ax.step(np.r_[BE[:-1], BE[-1]], np.r_[y, y[-1]], where='post', **kw)
n_core = None
lab = lambda d, p: next(r for r in [None] if r is None)

fig, axs = plt.subplots(4, 1, figsize=(7.4, 10.6), sharex=True)
fig.subplots_adjust(left=0.10, right=0.98, top=0.975, bottom=0.25, hspace=0.42)
panels = [('D', 'DS', 'debris drift alone', 'all evidence: core + drift + searched areas'),
          ('S', 'DS', 'searched areas alone', 'all evidence: core + drift + searched areas'),
          ('P', 'DSP', 'Pleiades objects alone, if they are aircraft debris', 'all evidence, if the objects are aircraft debris'),
          ('A', 'AS', 'drift with no finds in Australia alone (sensitivity)', 'all evidence with no finds in Australia')]
for k, (ax, (E, allp, ename, aname)) in enumerate(zip(axs, panels)):
    core = np.array(C0['core']['bands']); a2 = np.array(C0['a_' + E]['bands']); se = np.array(B0['a_' + E]['band_se'])
    a1 = vi_bands(E); ce = np.array(C0[E]['bands']); al = np.array(C0[allp]['bands'])
    ax.fill_between(np.r_[BE[:-1], BE[-1]], np.r_[core, core[-1]], step='post', color=GREY, alpha=0.45, lw=0, label='core: satellite + aircraft + end of flight')
    step(ax, a2, color=COL[E], lw=1.6, label='this evidence alone (reweighted samples, ±2 SE)')
    ax.errorbar(BM, a2, yerr=2 * se, fmt='none', ecolor=COL[E], elinewidth=0.7, capsize=0)
    ax.plot(np.r_[BE[:-1], BE[-1]] , np.r_[a1, a1[-1]], drawstyle='steps-post', color=COL[E], lw=1.0, ls=(0, (3, 2)), label='this evidence alone (module surface on the arc)')
    step(ax, ce, color=COL[E], lw=0.9, alpha=0.55, label='core + this evidence')
    step(ax, al, color=BLACK, lw=1.3, label=aname)
    med_a, med_c, med_all = C0['a_' + E]['median'], C0['core']['median'], C0[allp]['median']
    sh = C0['a_' + E]['vs_core']['median_shift_nm']; ler = C0['a_' + E]['lnER_core_vs_uniform']
    ax.set_title(f'{ename[0].upper() + ename[1:]}: median {abs(med_a):.1f} S, {abs(sh):.0f} NM {"north" if sh > 0 else "south"} of the core median; '
                 f'ln evidence ratio, core against uniform, {ler:+.2f}', loc='left', fontsize=8)
    ax.set_ylabel('probability per 1 deg band'); ax.set_xlim(-48, -10); ax.set_ylim(0, None); ax.margins(y=0.04)
    ax.legend(loc='upper right', frameon=False, fontsize=6.3, handlelength=2.2, bbox_to_anchor=(1.0, 1.0))
    ax.text(-0.075, 1.05, 'abcd'[k], transform=ax.transAxes, fontweight='bold', fontsize=10, va='bottom')
axs[-1].set_xlabel('impact latitude (deg; negative = south)')
ess = {E: RJ['cells']['head|D0|mix']['a_' + E]['ESS'] for E in 'DSPA'}
lost = C0['a_D']['uniform_share_unreachable']; se_ = RJ['meta']['arc']['span_ends_latlon']; span = (se_[0][0], se_[1][0])
f1 = ('Plain English. Each panel shows one type of evidence. Grey: the impact position from the satellite data, the aircraft performance '
      'model and the end-of-flight model (all four flight families, mixed by their probability). Coloured step line: the same evidence alone, with every '
      f'position on the 7th arc at 00:19:29 equally probable before the evidence ({abs(span[0]):.1f}-{abs(span[1]):.1f} S, the reach of the run J flight paths); the end-of-flight model then gives the impact. The samples for this '
      'line come from the satellite result, so few samples carry the north: bars show 2 standard errors from the seed scatter. Dashed: the module surface along the arc, '
      'with one fixed end-of-flight displacement. Black: all evidence together. The 00:19 data are held out. The 00:19 log-on cause: fuel exhaustion or another '
      'cause (prior odds 1 to 3); under the other cause the aircraft is silent. The end-of-flight physics is not calibrated. Searched areas use the impact point, not the seabed. '
      'Hydroacoustics gives no contribution. The Pleiades and the Australian panels are conditional or sensitivity results, not headline: a conditional PDF carries no Bayes factor.')
f2 = ('Technical. Core run J (tag run-j 1244b7c), four strata mixed by core P(family) at equal prior (waypoints 0.9982); EoF run J run-i-dive recipe, round-3 laws, '
      'bank limit U[52,90]; cell \'D0 total q=0.333 (C2 silent)\' via option_table_0019.seed_terms; seeds pooled by evidence. Drift: run A rebuilt node surfaces, 50 km kernel, '
      'GLORYS12V1 + ERA5 and GlobCurrent + ERA5 (product-relative windage), equal prior, marginalised jointly with Pleiades per row; nine finds. Searched areas: seabed_loglik.py '
      '(lib.rs transcription), rho 0.05, Phase 2 q 0.945, Bluefin-21 q 0.9; Ocean Infinity layers excluded. Pleiades: joint-surface-rho0.25-gcrel (P + COSMO F1-F4). '
      'Australian term: populated coasts, reconstructed law (k, c refitted), post hoc. Not-computed rows carried at the (seed, option) mean (ruling 15 Oct). '
      f'Reweighted views: r = u/q per 10 NM bin of the 00:19:29 arc position (circle about 0.57 N 64.25 E, radius 44.50 deg); Kish ESS drift {ess["D"]:.0f}, searches {ess["S"]:.0f}, Pleiades {ess["P"]:.0f}, Australian {ess["A"]:.0f}; '
      f'{100 * lost:.1f} % of the arc span has no proposal mass. Run J split-half accepted as a PASS by project ruling, 16 Oct 2026.')
fig.text(0.04, 0.155, f1, fontsize=6.0, wrap=True, va='top', ha='left'); fig.text(0.04, 0.065, f2, fontsize=5.6, wrap=True, va='top', ha='left', color='#333333')
fig.savefig(OUT / 'fig1-evidence-alone-along-arc.png', dpi=200); fig.savefig(OUT / 'fig1-evidence-alone-along-arc.pdf')
print('fig1 done')

# ---------------- Figure 2: disagreement and influence table (00:19 data held out, mixture) + ln evidence ratio per option
fig = plt.figure(figsize=(7.4, 6.4)); fig.subplots_adjust(left=0.03, right=0.98, top=0.95, bottom=0.25)
axT = fig.add_axes([0.02, 0.56, 0.96, 0.36]); axT.axis('off')
axB = fig.add_axes([0.10, 0.335, 0.86, 0.15])
EN = [('D', 'DS', 'debris drift (finds)'), ('S', 'DS', 'searched areas'), ('P', 'DSP', 'Pleiades objects, if aircraft debris'), ('A', 'AS', 'drift, no Australian finds (sens.)')]
hdr = ['evidence', 'median\nalone\n(deg)', 'ln evidence\nratio, core\nvs uniform', 'Bhatta-\ncharyya,\ncore vs alone', 'core mass\nin alone\n90 % HPD', 'alone mass\nin core\n90 % HPD',
       'median\nshift, alone\n- core (NM)', 'KL when\nremoved\nfrom all', 'share of\nall KL', 'median\nshift on\nremoval (NM)']
cells = []
for E, allp, nm in EN:
    a = C0['a_' + E]; v = a['vs_core']; lo = C0['loo'][f'{E}|{allp}']
    cells.append([nm, f'{a["median"]:.1f}', f'{a["lnER_core_vs_uniform"]:+.2f}', f'{v["bhattacharyya"]:.2f}', f'{v["mass_a_in_b"]:.2f}', f'{v["mass_b_in_a"]:.2f}',
                  f'{v["median_shift_nm"]:+.0f}', f'{lo["KL_all_vs_loo"]:.2f}', f'{lo["KL_share_of_total"]:.2f}' + (' *' if lo['flag_KL_gt_half'] else ''), f'{lo["median_shift_on_removal_nm"]:+.0f}'])
cells.append(['hydroacoustics', '-', '0 (no data)', '-', '-', '-', '-', '0', '0', '0'])
tb = axT.table(cellText=cells, colLabels=hdr, loc='center', cellLoc='center', colLoc='center', colWidths=[0.235] + [0.085] * 9)
tb.auto_set_font_size(False); tb.set_fontsize(6.3); tb.scale(1, 2.1)
for (i, j), c in tb.get_celld().items():
    c.set_linewidth(0.4); c.set_edgecolor('#bbbbbb')
    if i == 0: c.set_facecolor('#eeeeee'); c.set_height(c.get_height() * 1.9)
    if j == 0 and i > 0: c.get_text().set_ha('left')
axT.set_title('Each evidence type alone against the core, and its influence on all evidence (00:19 data held out)', loc='left', fontsize=8)
axT.text(-0.015, 1.04, 'a', transform=axT.transAxes, fontweight='bold', fontsize=10, ha='right')
xs = np.arange(6)
for k, (E, allp, nm) in enumerate(EN):
    y = [RJ['cells'][f'head|D{d}|mix']['a_' + E]['lnER_core_vs_uniform'] for d in range(6)]
    axB.plot(xs + (k - 1.5) * 0.08, y, 'o-', color=COL[E], ms=3.5, lw=0.9, label=nm)
axB.axhline(0, color='#888888', lw=0.6); axB.set_xticks(xs); axB.set_xticklabels([DN[f'D{d}'] for d in range(6)], fontsize=6)
axB.set_ylabel('ln evidence ratio\ncore vs uniform'); axB.legend(frameon=False, fontsize=6, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.32))
axB.set_title('The sign of each ratio is the same for all six 00:19 treatments', loc='left', fontsize=8)
axB.text(-0.09, 1.08, 'b', transform=axB.transAxes, fontweight='bold', fontsize=10)
axB.text(1.0, 1.02, 'above 0 = evidence favours the core region', transform=axB.transAxes, ha='right', fontsize=6)
g1 = ('Plain English. "Alone" means the evidence with every position on the 7th arc equally probable before it. The ln evidence ratio compares how well this evidence '
      'agrees with the core result and with a position anywhere along the arc: below 0, the evidence prefers other parts of the arc. The Bhattacharyya value is 1 when two PDFs '
      'are the same and 0 when they do not overlap. KL removed from all: how much the all-evidence PDF changes when this evidence is removed. * = more than half of the change '
      'that all the evidence makes to the core. Pleiades and the Australian term are conditional or sensitivity results. A conditional PDF carries no Bayes factor.')
g2 = ('Technical. Run J, four strata by core P(family), cell D0 total q=1/3 (C2 silent); D3/D4 waypoints from the both-burst supplementary pass. ln ER = ln E_core[L_E] - ln E_U[L_E], '
      'U = uniform per NM of 00:19:29 arc position (40.6-11.8 S), same end-of-flight model; not-computed rows carried at each base\'s own mean. KL(all||all-E) = '
      'E_all[ln L_E] - ln(Z_all/Z_all-E); all = core x drift x searches (unconditional) or x Pleiades (conditional on H). HPD on the 769 km2 equal-area grid. Drift 50 km kernel, '
      'two ocean models jointly with Pleiades; searches rho 0.05 at the impact point; Australian term reconstructed (post hoc). Hydroacoustics 0 by ruling (no P_D).')
fig.text(0.03, 0.19, g1, fontsize=6.0, wrap=True, va='top'); fig.text(0.03, 0.085, g2, fontsize=5.6, wrap=True, va='top', color='#333333')
fig.savefig(OUT / 'fig2-disagreement-influence.png', dpi=200); fig.savefig(OUT / 'fig2-disagreement-influence.pdf'); print('fig2 done')

# ---------------- Figure 3: HPD regions on the equal-area grid, core vs all, with searched ground and the arc line
MP = np.load(OUT / 'maps-D0-mix.npz'); import views_lib as VL
spec = importlib.util.spec_from_file_location('seabed_loglik', str(PROJ / 'results/composer-pass1-run-c/seabed_loglik.py'))
SL = importlib.util.module_from_spec(spec); spec.loader.exec_module(SL); SL.COV = PROJ / 'engine/hypotheses/seabed-search/coverage'
la_, lo_ = np.meshgrid(np.arange(-41, -24, 0.03), np.arange(86, 108, 0.03), indexing='ij')
R_ = [(SL.decode(SL.COV / f'{n}.cov'), q) for n, q in SL.CAMPAIGNS]
cu = 1 - np.prod([1 - SL.coverage(Rr, la_.ravel(), lo_.ravel()) for Rr, q in R_], 0).reshape(la_.shape)
fig, axs = plt.subplots(1, 2, figsize=(7.4, 6.2), sharey=True); fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.33, wspace=0.05)
yc = V.ROW_MID; xc = V.LON0 + (np.arange(V.NX) + 0.5) * V.STEP
for k, (ax, (pa, pb, ta, tb_, ttl)) in enumerate(zip(axs, [('core', 'DS', 'core', 'all evidence', 'All evidence: the 90 % region extends north'),
                                                          ('core', 'DSP', 'core', 'all evidence, if the Pleiades objects are debris', 'If the Pleiades objects are debris: near 35 S')])):
    for p, col, lab in ((pa, GREY, ta), (pb, '#1f5fa8' if pb == 'DS' else COL['P'], tb_)):
        m = MP[p].astype(float); M = m.reshape(V.NY, V.NX)
        for lv, lw_, ls_ in ((0.9, 1.0, '-'), (0.5, 1.6, '-')):
            mk = VL.hpd_mask(m, lv).reshape(V.NY, V.NX).astype(float)
            ax.contour(xc, yc, mk, levels=[0.5], colors=[col], linewidths=lw_)
        ax.plot([], [], color=col, lw=1.3, label=f'{lab}: 50 % (thick) and 90 % (thin) HPD')
    ax.contourf(lo_[0], la_[:, 0], cu, levels=[0.5, 1.01], colors=['#d9b98c'], alpha=0.45)
    ax.plot([], [], color='#d9b98c', lw=6, alpha=0.6, label='searched seabed (Phase 2 and Bluefin-21)')
    aL, aO = V.arc_point(np.arange(800, 2400, 5.0)); ax.plot(aO, aL, color='#555555', lw=0.7, ls=':'); ax.plot([], [], color='#555555', lw=0.7, ls=':', label='7th arc (00:19:29, fitted to run J)')
    ax.set_xlim(86, 106); ax.set_ylim(-41, -25); ax.set_xlabel('longitude (deg E)'); ax.set_aspect(1 / np.cos(np.radians(33)))
    ax.set_title(ttl, loc='left', fontsize=8); 
    ax.text(-0.10 if k == 0 else -0.05, 1.03, 'ab'[k], transform=ax.transAxes, fontweight='bold', fontsize=10, ha='right')
    a90 = C0[pb]['hpd90_km2'] / 1e3; c90 = C0['core']['hpd90_km2'] / 1e3
    ax.text(0.02, 0.97, f'90 % area: core {c90:.0f}k km2, {tb_.split(":")[0]} {a90:.0f}k km2\non searched ground: core {C0["core"]["p_on_searched_ground"]:.2f}, this {C0[pb]["p_on_searched_ground"]:.2f}',
            transform=ax.transAxes, va='top', fontsize=6)
axs[0].set_ylabel('latitude (deg)')
hh, ll = [], []
for ax in axs:
    for h_, l_ in zip(*ax.get_legend_handles_labels()):
        if l_ not in ll: hh.append(h_); ll.append(l_)
fig.legend(hh, ll, loc='lower center', bbox_to_anchor=(0.5, 0.245), ncol=2, frameon=False, fontsize=6)
h1 = ('Plain English. Regions that hold 50 % and 90 % of the probability of the impact position. Grey: satellite data, aircraft performance and end of flight (core). Blue: with the '
      'debris drift (nine finds, two ocean models) and the searched areas. Purple: also with the Pleiades objects, on the condition that they are aircraft debris (a conditional '
      'result). Tan: seabed searched by Phase 2 and Bluefin-21. 00:19 data held out; cause of the 00:19 log-on: fuel exhaustion or another cause with the aircraft silent '
      '(prior odds 1 to 3). Positions are impact points, not seabed points. The end-of-flight physics is not calibrated. Ocean Infinity areas are not used.')
h2 = ('Technical. Run J, four strata by core P(family); cell D0 total q=1/3 (C2 silent). Equal-area grid 0.25 deg x authalic q step, 769.3 km2 cells; HPD = smallest cell set. '
      'Drift run A rebuilt surfaces 50 km, GLORYS12V1/GlobCurrent + ERA5 at equal prior, marginalised jointly with Pleiades (rho 0.25, gcrel, P + COSMO F1-F4). Searches '
      'seabed_loglik.py rho 0.05 (Phase 2 q 0.945, Bluefin-21 q 0.9); tan = union coverage >= 0.5. No settling resample on run J. Run J split-half accepted as a PASS by project ruling, 16 Oct 2026; '
      'north of 33 S under-sampled (see note). Not-computed rows carried at the (seed, option) mean.')
fig.text(0.03, 0.20, h1, fontsize=6.0, wrap=True, va='top'); fig.text(0.03, 0.095, h2, fontsize=5.6, wrap=True, va='top', color='#333333')
fig.savefig(OUT / 'fig3-hpd-map-core-vs-all.png', dpi=200); fig.savefig(OUT / 'fig3-hpd-map-core-vs-all.pdf'); print('fig3 done')
