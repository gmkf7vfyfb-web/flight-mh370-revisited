"""Composer views on run J, step 3c: markdown tables for the note, from views-run-j.json. Usage: python report_note_tables.py OUTDIR"""
import sys, json, pathlib, numpy as np
OUT = pathlib.Path(sys.argv[1]); RJ = json.load(open(OUT / 'views-run-j.json'))
DK = [f'D{d}' for d in range(6)]
DN = {'D0': "D0' 00:19 data held out", 'D1': 'D1 00:19:29 BTO', 'D2': 'D2 00:19:29 BTO + BFO', 'D3': 'D3 both BFOs as recorded',
      'D4': 'D4 both BFOs, shared start-up offset', 'D5': 'D5 00:19:37 BFO with start-up offset'}
EN = {'D': 'debris drift (finds)', 'S': 'searched areas', 'P': 'Pléiades (conditional on H)', 'A': 'drift + Australian non-recovery (SENSITIVITY)'}
ALLP = {'D': 'DS', 'S': 'DS', 'P': 'DSP', 'A': 'AS'}; LOOP = {'D': 'S', 'S': 'D', 'P': 'DS', 'A': 'S'}
k = lambda x: '' if x is None else f'{x / 1e3:.0f}k'
f2 = lambda x, n=2: '' if x is None else f'{x:.{n}f}'
L = []
def boot(d, p):
    return RJ['boot'][d].get(p, {})
def labn(d, p):
    c = RJ['cells'][f'head|{d}|mix'][p]; b = boot(d, p); ni = b.get('implied_n_north_of_33S')
    vals = [v for v in ((ni * c['north_of_33S']) if ni else None, c.get('kish_ess_north_of_33S')) if v is not None]
    return min(vals) if vals else None
for d in DK:
    C = RJ['cells'][f'head|{d}|mix']
    L.append(f'\n#### {DN[d]} — four-stratum mixture, cause model q = 1/3 (other cause silent)\n')
    L.append('| evidence E | view | median lat | median along arc (NM from S tip) | 50 % / 90 % HPD km² | mass N of 33 S | effective sample N of 33 S | Kish ESS | on searched ground |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    c0 = C['core']
    L.append(f"| core (satcom + flight + EoF) | = view (a) for the core | {f2(c0['median'])} | {f2(c0.get('median_arc_nm'), 0)} | {k(c0['hpd50_km2'])} / {k(c0['hpd90_km2'])} | {f2(c0['north_of_33S'], 3)} | {f2(labn(d, 'core'), 0)} | {c0['ESS']:.3g} | {f2(c0.get('p_on_searched_ground'))} |")
    for E in 'DSPA':
        a = C['a_' + E]; vi = a.get('view_i') or {}
        L.append(f"| {EN[E]} | (a)(i) module surface on the arc | {f2(vi.get('median_lat'))} | {f2(vi.get('median_arc_nm'), 0)} | – | {f2(vi.get('north_of_33S'), 3)} | (no sampling) | – | – |")
        L.append(f"| | (a)(ii) alone, reweighted run J | {f2(a['median'])} | {f2(a.get('median_arc_nm'), 0)} | {k(a['hpd50_km2'])} / {k(a['hpd90_km2'])} | {f2(a['north_of_33S'], 3)} | {f2(labn(d, 'a_' + E), 0)} | {a['ESS']:.3g} | {f2(a.get('p_on_searched_ground'))} |")
        for lab, p in (('(b) core + E', E), ('(c) all except E', LOOP[E]), ('all' + (' | H' if E == 'P' else ' (with Australian term)' if E == 'A' else ''), ALLP[E])):
            x = C[p]
            L.append(f"| | {lab} | {f2(x['median'])} | {f2(x.get('median_arc_nm'), 0)} | {k(x['hpd50_km2'])} / {k(x['hpd90_km2'])} | {f2(x['north_of_33S'], 3)} | {f2(labn(d, p), 0)} | {x['ESS']:.3g} | {f2(x.get('p_on_searched_ground'))} |")
    L.append('| hydroacoustics | all views | contributes nothing (0 by ruling, no P_D) | | | | | | |')
    L.append('\n| E | ln ER (a) vs core, (ii) / (i) | 90 % HPD: core mass in (a) / (a) mass in core | Bhattacharyya (a) vs core | median shift (a) − core, NM | ln E[L_E given all others] (c→all) | Bhattacharyya (c) vs all | KL(all ‖ all−E) nats / share of KL(all ‖ core) | Δ median, Δ 90 % area on removal |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for E in 'DSPA':
        a = C['a_' + E]; v = a['vs_core']; lo = C['loo'][f'{E}|{ALLP[E]}']
        L.append(f"| {EN[E]} | {a['lnER_core_vs_uniform']:+.2f} / {(a.get('lnER_core_vs_uniform_i') or float('nan')):+.2f} | {v['mass_a_in_b']:.2f} / {v['mass_b_in_a']:.2f} | {v['bhattacharyya']:.2f} | {f2(v['median_shift_nm'], 0)} | {lo['lnE_E_given_others']:+.2f} ({lo['lnER_vs_uniform']:+.2f} vs uniform) | {lo['bhattacharyya']:.2f} | {lo['KL_all_vs_loo']:.2f} / {lo['KL_share_of_total']:.2f}{' **>0.5**' if lo['flag_KL_gt_half'] else ''} | {f2(lo['median_shift_on_removal_nm'], 0)} NM, {lo['hpd90_change_on_removal_km2'] / 1e3:+.0f}k km² |")
# per-option headline
L.append('\n#### Headline products across the six 00:19 options (mixture)\n')
L.append('| option | product | median lat (± seed SE) | 5 / 95 % lat | 50 / 90 / 95 % HPD km² | N of 33 S (± SE) | effective sample N of 33 S | ESS | on searched ground | waypoints share | A1 / A2 / B |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|')
PNM = {'core': 'core', 'DS': 'ALL', 'DSP': 'ALL given H (conditional)', 'AS': 'ALL + Australian term (sensitivity)'}
for d in DK:
    for p, nm in PNM.items():
        x = RJ['cells'][f'head|{d}|mix'][p]; b = boot(d, p); fs = x.get('family_share', {})
        L.append(f"| {d} | {nm} | {x['median']:.2f} ± {f2(b.get('median_se'), 2)} | {x['q05']:.2f} / {x['q95']:.2f} | {k(x['hpd50_km2'])} / {k(x['hpd90_km2'])} / {k(x['hpd95_km2'])} | {x['north_of_33S']:.3f} ± {f2(b.get('north33_se'), 3)} | {f2(labn(d, p), 0)} | {x['ESS']:.3g} | {x['p_on_searched_ground']:.3f} | {x['stratum_share']['run-j-waypoints']:.4f} | {fs.get('A1', 0):.2f} / {fs.get('A2', 0):.2f} / {fs.get('B', 0):.2f} |")
# per family
L.append('\n#### Per end-of-flight family (D0\' and D4), before the mixture\n')
L.append('| option | family | product | median lat | 90 % HPD km² | N of 33 S | ESS | (a)(ii) drift alone median | (a)(ii) searches alone median |')
L.append('|---|---|---|---|---|---|---|---|---|')
for d in ('D0', 'D4'):
    for fam in ('A1', 'A2', 'B'):
        C = RJ['cells'][f'head|{d}|{fam}']
        for p in ('core', 'DS', 'DSP'):
            x = C[p]
            L.append(f"| {d} | {fam} | {PNM[p]} | {x['median']:.2f} | {k(x['hpd90_km2'])} | {x['north_of_33S']:.3f} | {x['ESS']:.3g} | {C['a_D']['median']:.2f} | {C['a_S']['median']:.2f} |")
# per stratum
L.append('\n#### Per flight family (core stratum), D0\'\n')
L.append('| stratum | core median | ALL median | ALL 90 % HPD km² | ALL N of 33 S | ALL ESS | share of ALL |')
L.append('|---|---|---|---|---|---|---|')
for st in ('run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb'):
    C = RJ['cells'][f'head|D0|{st}']; sh = RJ['cells']['head|D0|mix']['DS']['stratum_share'][st]
    L.append(f"| {st} | {C['core']['median']:.2f} | {C['DS']['median']:.2f} | {k(C['DS']['hpd90_km2'])} | {C['DS']['north_of_33S']:.3f} | {C['DS']['ESS']:.3g} | {sh:.4f} |")
# modes
L.append('\n#### Modes along the arc (impact latitude; D0\', mixture; basins of the 0.15 deg-smoothed PDF with mass ≥ 0.001)\n')
L.append('| product | modes: peak latitude (mass) |'); L.append('|---|---|')
for p in ('core', 'DS', 'DSP', 'AS'):
    ms = RJ['cells']['head|D0|mix'][p]['modes']
    L.append(f"| {PNM[p]} | " + '; '.join(f"{m['peak_lat']:.2f} ({m['mass']:.3f})" for m in ms) + ' |')
# sensitivities
L.append('\n#### Labelled sensitivities on ALL (mixture)\n')
L.append('| option | variant | median lat | 90 % HPD km² | N of 33 S | on searched ground |'); L.append('|---|---|---|---|---|---|')
SV = {'DS': 'headline ALL', 'D100S': 'drift model error doubled (kernel 50 → 100 km)', 'DS10': 'searched-areas model error doubled (rho 0.05 → 0.10)',
      'DGS': 'drift GLORYS12 only', 'DCS': 'drift GlobCurrent only', 'AS': 'Australian populated-coast non-recovery added'}
for d in ('D0', 'D2', 'D4'):
    for p, nm in SV.items():
        x = RJ['cells'][f'head|{d}|mix'][p]
        L.append(f"| {d} | {nm} | {x['median']:.2f} | {k(x['hpd90_km2'])} | {x['north_of_33S']:.3f} | {x['p_on_searched_ground']:.3f} |")
for d in ('D3', 'D4'):
    for p in ('core', 'DS'):
        x = RJ['cells'][f'prodonly|{d}|mix'][p]; y = RJ['cells'][f'head|{d}|mix'][p]
        L.append(f"| {d} | {PNM[p]}: production 24 seeds only (headline uses the both-burst supplementary waypoints) | {x['median']:.2f} (headline {y['median']:.2f}) | {k(x['hpd90_km2'])} ({k(y['hpd90_km2'])}) | {x['north_of_33S']:.3f} ({y['north_of_33S']:.3f}) | {x['p_on_searched_ground']:.3f} |")
# not computed
L.append('\n#### Not-computed share of the core weight, per factor column and 00:19 option\n')
cols = sorted({kk.split('|')[2] for kk in RJ['not_computed']})
L.append('| option | ' + ' | '.join(cols) + ' |'); L.append('|---' * (len(cols) + 1) + '|')
for d in DK:
    L.append(f'| {d} | ' + ' | '.join(f"{RJ['not_computed'].get(f'head|{d}|{c}', float('nan')):.2e}" for c in cols) + ' |')
# coverage ESS per 5 deg
L.append('\n#### Effective sample per 5° latitude band (D0\', mixture): min(seed-scatter implied × band mass, Kish within band)\n')
bands = [str(lo) for lo in range(-50, -5, 5)]
L.append('| product | ' + ' | '.join(f'{int(b)}…{int(b) + 5}' for b in bands) + ' |'); L.append('|---' * (len(bands) + 1) + '|')
BE = np.arange(-50, -5, 1.0)
for p in ('core', 'DS', 'DSP', 'AS', 'a_D', 'a_S', 'a_P', 'a_A'):
    x = RJ['cells']['head|D0|mix'][p]; b = boot('D0', p); row = []
    for lo in bands:
        m = sum(x['bands'][i] for i, a in enumerate(BE[:-1]) if int(lo) <= a < int(lo) + 5); ni = (b.get('implied_n_by_5deg') or {}).get(lo)
        kk = x['kish_ess_by_5deg'].get(lo, 0.0); v = min([v for v in (ni * m if ni else None, kk) if v is not None]) if m > 0.01 else None
        row.append('–' if m <= 0.01 else f'{v:.0f} (m {m:.2f})')
    L.append(f'| {p} | ' + ' | '.join(row) + ' |')
open(OUT / 'note-tables.md', 'w').write('\n'.join(L)); print('wrote', len(L), 'lines')
