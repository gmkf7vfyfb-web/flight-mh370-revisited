"""Dedicated-run figure redrawn for 20-40 S (panels a and b). Run after merge_arclat.py in the same kernel/session:
exec(open('fig_arclat.py').read()) with N, prof, POST, cl, hw, TITLE_A, TITLE_B, OUT defined."""
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt

apply_figure_style(sizes=(8, 7, 6))
col = {'finds only': '#555555', 'C (low detection)': '#2a7ab0', 'populated coast only': '#7b4fa0', 'B (primary)': '#d35400'}
lab = {'finds only': 'Finds only (base setting)',
       'C (low detection)': 'Finds + no finds in Australia, low detection (option C)',
       'populated coast only': 'Finds + no finds on populated Australian coast only',
       'B (primary)': 'Finds + no finds in Australia, pre-registered detection (option B)'}
ORDER = ['finds only', 'C (low detection)', 'populated coast only', 'B (primary)']
fig, axs = plt.subplots(2, 1, figsize=(7.2, 8.0), sharex=True, gridspec_kw=dict(hspace=0.2, height_ratios=[1.1, 1]))
ax = axs[0]
ax.axvspan(19.6, 25.6, color='0.93', lw=0, zorder=0)
ax.text(22.6, 0.98, 'New points (20 Oct)', transform=ax.get_xaxis_transform(), ha='center', va='top', fontsize=6, color='0.35')
t = prof[prof.position == 'track'].sort_values('arc_lat')
for o in ORDER:
    ax.errorbar(-t.arc_lat, t[o], yerr=2 * t[o + '_sd'], color=col[o], lw=1.6 if o == 'finds only' else 1.1,
                marker='o', ms=2.5, capsize=0, elinewidth=0.8, label=lab[o], zorder=3 if o == 'finds only' else 2)
    if o == 'finds only':
        pv = prof.pivot_table(index='arc_lat', columns='position', values=o).sort_index()
        ax.fill_between(-pv.index, pv.min(1), pv.max(1), color=col[o], alpha=0.15, lw=0,
                        label='Finds only, range over the track and 50 NM either side')
if OV_PTS is not None:
    for o in ORDER:
        ax.plot([26.0], [OV_PTS[o]], marker='D', mfc='none', mec=col[o], ms=4.5, ls='none', zorder=4)
    ax.plot([], [], marker='D', mfc='none', mec='0.3', ms=4.5, ls='none', label='26° S repeat (new run, same points)')
ax.axhline(0, color='0.85', lw=0.6, zorder=0)
ax.set_ylabel('Log-likelihood relative to maximum')
ax.set_title(TITLE_A, loc='left')
ax.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.6, 0.0), fontsize=6.3)
ax = axs[1]
bw = 0.5; e2 = np.arange(-42, -18.9, bw); cen = -(e2[:-1] + bw / 2)
dens = lambda p: np.histogram(cl, e2, weights=p)[0] / bw
ax.axvspan(19.6, 25.6, color='0.93', lw=0, zorder=0)
ax.plot(cen, dens(hw / hw.sum()), color='k', lw=1.6, label='Flight path only (00:19 data not used)')
for o in ORDER:
    ax.plot(cen, dens(POST[(o, 'mean')]), color=col[o], lw=1.6 if o == 'finds only' else 1.1,
            ls='--' if o == 'finds only' else '-', label='Flight path and ' + lab[o][0].lower() + lab[o][1:])
ax.plot(-dv.latitude_deg, dv.density_per_deg, color='0.55', lw=0.9, ls=':', label='Davey et al. (2016), Fig. 10.3')
ax.set_ylabel('Probability density (per degree)')
ax.set_xlabel('Latitude on the 7th arc (° S)')
ax.set_xlim(41, 19.3)
ax.set_title(TITLE_B, loc='left')
ax.legend(frameon=False, loc='upper right', fontsize=6.3)
for a, l in zip(axs, 'ab'):
    panel_letter(a, l)
fig.text(0.01, 0.004, FOOT, fontsize=5.5, wrap=True, va='bottom', ha='left')
fig.subplots_adjust(bottom=0.215, top=0.965, left=0.1, right=0.98)
fig.savefig(f'{OUT}.png', dpi=200)
fig.savefig(f'{OUT}.pdf')
r = fig.canvas.get_renderer()
texts = [(tt, tt.get_window_extent(r)) for tt in fig.findobj(mpl.text.Text) if tt.get_text().strip() and tt.get_visible()]
ov = [(a.get_text()[:30], b.get_text()[:30]) for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
print('text overlaps:', ov)
