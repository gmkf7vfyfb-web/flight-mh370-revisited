"""Figures for the 8 Nov 2026 drift analysis. Working versions (colour, notes beneath) and Journal of Navigation versions
(greyscale, no title, no notes, 127 mm wide, 600 dpi PNG for Word, PDF, proof with caption beneath, caption text file)."""
import os, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
OUT = 'figs'; os.makedirs(OUT, exist_ok=True)
F = pd.read_csv('res-final/final-posterior-summaries.csv'); F0 = F[F.core == 'H_D0_all']
D = pd.read_csv('res-final/latitude-densities.csv'); x = 0.5 * (D.lat_lo + D.lat_hi)
H = 'HEADLINE: twelve non-circular items, identity-weighted'
def sh(v, c): r = F0[(F0.variant == v) & (F0.case == c)]; assert len(r) == 1, (v, c); return float(r['shift'].iloc[0])
R3 = 'R3-allcoasts-4periods'
NOTES = ("Notes. Core: satellite communication and flight-performance posterior of end-of-flight run J, with the 00:19 data held out. "
 "Drift: two ocean models with equal weight (GLORYS12V1 currents at 0.494 m with ERA5 wind; Copernicus GlobCurrent surface currents with ERA5 wind; "
 "the GlobCurrent wind factor is reduced by 0.60 to 0.75 per cent for its built-in wind drift). Flaperon response as measured by CSIRO (1.2 per cent "
 "wind factor, 0.10 m/s leeway); other exterior panels 1.2 +/- 0.3 per cent; interior panels median 2.5 per cent. 84 release points along the 7th arc; "
 "6250 particles per object type and per ocean sample; 16 ocean samples, 32 south of 33.25 S. Finds scored to 30 Jan 2017 within 50 km of the find "
 "place; delay from arrival to find exponential, mean 60 days. Detection levels log-normal (sigma 1) per coast and period, 16384 draws. "
 "Coasts: Reunion, Mauritius and Rodrigues, Mozambique, South Africa, Madagascar, Pemba and the rest of East Africa, Comoros, Seychelles. "
 "Coasts with few people or little searching start at 0.3 of the level of the find coasts. Australian coasts carry no information unless stated. "
 "Twelve items: the nine finds of Durgadoo et al. and Linga Linga, Nautilus Bay and Mpame, weighted by their identification grade "
 "(confirmed 1, almost certain 0.98, highly likely 0.9). Not used: items identified partly from drift (sensitivity only), Sandravinany (date range "
 "past the window), coasts in Asia. Provisional physics; Monte Carlo uncertainty of the mean about 0.2 degrees.")
def finish(fig, stem, grey, cap):
    if grey:
        fig.savefig(f'{OUT}/{stem}-jon-word.png', dpi=600); fig.savefig(f'{OUT}/{stem}-jon.pdf'); plt.close(fig)
        open(f'{OUT}/{stem}-jon-caption.txt', 'w').write(cap + '\n')
        img = plt.imread(f'{OUT}/{stem}-jon-word.png'); hh, ww = img.shape[:2]; W = 127 / 25.4; Hh = W * hh / ww; capH = 0.16 * len(textwrap.wrap(cap, 98)) + 0.2
        f2 = plt.figure(figsize=(W, Hh + capH)); a = f2.add_axes([0, capH / (Hh + capH), 1, Hh / (Hh + capH)]); a.imshow(img); a.axis('off')
        f2.text(0.02, (capH - 0.08) / (Hh + capH), '\n'.join(textwrap.wrap(cap, 98)), fontsize=6.3, va='top'); f2.savefig(f'{OUT}/{stem}-jon-proof.pdf'); plt.close(f2)
    else:
        fig.savefig(f'{OUT}/{stem}.png', dpi=200); fig.savefig(f'{OUT}/{stem}.pdf'); plt.close(fig)
plt.rcParams.update({'font.size': 7, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
# ---- Figure A: latitude density
CA = ("Probability density of the impact latitude on the 7th arc. Thin grey line: satellite communication and flight data only. "
      "Dashed line: with the drift evidence of the nine finds, as first scored (finds window to 30 January 2017, three detection periods, "
      "six find coasts). Thick line: with the drift evidence of twelve items on all western Indian Ocean coasts and four detection periods. "
      "Dotted line: the same, with no finds on Australian coasts (detection on populated Australian coasts 0.25 of that on the find coasts). "
      "Means: 36.72 degrees south (data only), "
      f"{-(-36.717 + sh('R0-module-run', 'ladder: nine finds')):.2f}, {-(-36.717 + sh(R3, H)):.2f} and {-(-36.717 + sh(R3, 'Australia ratio 0.25')):.2f} degrees south.")
def figA(grey):
    w = 127 / 25.4 if grey else 180 / 25.4; h = 2.9 if grey else 4.6
    fig, ax = plt.subplots(figsize=(w, h)); 
    if not grey: fig.subplots_adjust(bottom=0.36, top=0.9, left=0.08, right=0.98)
    else: fig.subplots_adjust(bottom=0.16, top=0.97, left=0.11, right=0.98)
    S = [('core', 'Satellite and flight data only', dict(color='0.55', lw=1.0, ls='-'), '#888888'),
         ('R0-module-run|ladder: nine finds', 'With drift: nine finds, six find coasts, three periods', dict(color='0.2', lw=1.0, ls='--'), '#4C72B0'),
         (f'{R3}|{H}', 'With drift: twelve items, all coasts, four periods', dict(color='0.0', lw=2.0, ls='-'), '#C44E52'),
         (f'{R3}|Australia ratio 0.25', 'Same, and no finds on Australian coasts', dict(color='0.15', lw=1.2, ls=':'), '#55A868')]
    for col, lab, st, c in S:
        kw = dict(st); 
        if not grey: kw['color'] = c
        ax.plot(-x, D[col], label=lab, **kw)
    ax.set_xlim(42, 24); ax.set_xlabel('Latitude on the 7th arc (degrees south)'); ax.set_ylabel('Probability density (per degree)')
    ax.set_ylim(0, None); ax.margins(x=0); ax.legend(frameon=False, loc='upper right')
    if not grey:
        ax.set_title('The drift evidence now moves the impact estimate slightly south, not north', loc='left', fontsize=8)
        fig.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTES, 175)), fontsize=5.2, va='bottom')
    return fig
for g in (False, True): finish(figA(g), 'drift-impact-latitude-density-2026-11-08', g, CA)
# ---- Figure B: ladder and sensitivities
rows = [('Model changes, one at a time (nine finds unless stated)', None),
        ('As first scored: to 30 Jan 2017, three periods, six find coasts', sh('R0-module-run', 'ladder: nine finds')),
        ('Window to 30 Jun 2016 (as on 7 Nov), this run', sh('R1-oldwindow', 'ladder: nine finds')),
        ('Fourth detection period from 1 Jul 2016', sh('R4-4periods', 'ladder: nine finds')),
        ('All western Indian Ocean coasts', sh('R2-allcoasts', 'ladder: nine finds')),
        ('All coasts and four periods', sh(R3, 'ladder: nine finds')),
        ('Headline: twelve items, weighted by identification grade', sh(R3, H)),
        ('Changes to the headline', None),
        ('All identification weights set to 1', sh(R3, 'all identity probabilities set to 1')),
        ('Add eight items identified partly from drift', sh(R3, 'add eight items identified partly from drift (sensitivity)')),
        ('Without Nautilus Bay and Mpame', sh(R3, 'without Nautilus Bay and Mpame')),
        ('Fresh arrival: flaperon and Mossel Bay 10 days, Paindane 14 days', sh(R3, 'time ashore: fresh marks 10 d, 10 d, 14 d')),
        ('Fresh arrival: flaperon and Mossel Bay 3 days, Paindane 14 days', sh(R3, 'time ashore: fresh marks 3 d, 3 d, 14 d')),
        ('Mossel Bay find dated at its second beaching (Mar 2016)', sh(R3, 'Mossel Bay at second beaching (21-22 Mar 2016)')),
        ('Official alternative dates (Vilanculos, Pemba, Mauritius)', sh(R3, 'three official alternative dates')),
        ('Other coasts at the level of the find coasts', sh(R3, 'other coasts at the find-coast level')),
        ('Other coasts at 0.1 of the level of the find coasts', sh(R3, 'other coasts at 0.1 of the find-coast level')),
        ('Populated new South African and Mozambique coasts at 0.3', sh(R3, 'populated new coasts also at 0.3')),
        ('No finds on Australian coasts, ratio 1', sh(R3, 'Australia ratio 1.0')),
        ('No finds on Australian coasts, ratio 0.25', sh(R3, 'Australia ratio 0.25')),
        ('No finds on Australian coasts, ratio 0.05', sh(R3, 'Australia ratio 0.05')),
        ('All items except Mossel Bay', sh(R3, 'all but Mossel Bay')),
        ('All items except Mossel Bay and Paindane', sh(R3, 'all but Mossel Bay and Paindane')),
        ('Mossel Bay only', sh(R3, 'only Mossel Bay')),
        ('Flaperon only', sh(R3, 'only the flaperon')),
        ('Find-place tolerance 25 km', sh(R3, 'kernel 25 km')), ('Find-place tolerance 100 km', sh(R3, 'kernel 100 km')), ('Find-place tolerance 200 km', sh(R3, 'kernel 200 km')),
        ('GlobCurrent ocean model only', float(F0[F0.case == f'{H} [globcurrent only]']['shift'].iloc[0])),
        ('GLORYS12 ocean model only', float(F0[F0.case == f'{H} [glorys12 only]']['shift'].iloc[0]))]
ha, hb = sh(R3, 'particle half a'), sh(R3, 'particle half b'); hd = sh(R3, H)
CB = ("Change in the mean impact latitude on the 7th arc caused by the drift evidence (degrees; positive is north). Upper group: the drift "
      "model changed one step at a time, from the model as first scored to the headline model. Lower group: changes to the headline model. "
      f"Grey band: half the difference between the two independent halves of the particles ({min(ha, hb):+.2f} and {max(ha, hb):+.2f} degrees) "
      "about the headline value, an indication of the Monte Carlo uncertainty. The mean with the satellite and flight data only is 36.72 degrees south.")
def figB(grey):
    n = len(rows); w = 127 / 25.4 if grey else 180 / 25.4; h = 0.135 * n + (0.45 if grey else 1.9)
    fig, ax = plt.subplots(figsize=(w, h))
    fig.subplots_adjust(left=0.56 if grey else 0.5, right=0.93 if grey else 0.96, top=1 - 0.12 / h if grey else 1 - 0.32 / h, bottom=(0.38 / h) if grey else (1.6 / h))
    y = np.arange(n)[::-1]
    ax.axvspan(hd - abs(ha - hb) / 2, hd + abs(ha - hb) / 2, color='0.88' if grey else '#f2d7d8', zorder=0, lw=0)
    ax.axvline(0, color='0.5', lw=0.6, zorder=1)
    for yi, (lab, v) in zip(y, rows):
        if v is None:
            ax.text(-0.02, yi, lab, transform=mpl.transforms.blended_transform_factory(ax.transAxes, ax.transData), ha='right', va='center', fontsize=5.6 if grey else 6.5, fontweight='bold'); continue
        head = lab.startswith('Headline')
        c = 'black' if grey else ('#C44E52' if head else '#333333')
        ax.plot([0, v], [yi, yi], color='0.6', lw=0.6, zorder=2); ax.plot(v, yi, 'o', ms=4.2 if head else 3.2, color=c, mfc=c if (head or not grey) else 'white', mec=c, zorder=3)
        ax.text(-0.02, yi, lab, transform=mpl.transforms.blended_transform_factory(ax.transAxes, ax.transData), ha='right', va='center', fontsize=5.2 if grey else 6)
    ax.set_yticks([]); ax.spines['left'].set_visible(False); ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel('Change in mean latitude (degrees north)' if grey else 'Change in mean impact latitude (degrees; positive is north)'); ax.set_xlim(-0.7, 1.25)
    if not grey:
        ax.set_title('The headline drift model moves the estimate slightly south; Mossel Bay alone, Australian non-finds and GLORYS12 alone move it north', loc='left', fontsize=7, x=-0.95)
        fig.text(0.01, 0.01, '\n'.join(textwrap.wrap(NOTES, 175)), fontsize=5.2, va='bottom')
    return fig
for g in (False, True): finish(figB(g), 'drift-impact-latitude-sensitivity-2026-11-08', g, CB)
print(CA); print(CB)
