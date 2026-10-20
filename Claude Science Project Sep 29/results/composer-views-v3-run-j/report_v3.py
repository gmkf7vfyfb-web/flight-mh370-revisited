"""Composer views v3: tables (products-v3.csv, influence-v3.csv, sensitivity-v3.csv, compare-v2-v3.csv, note-tables-v3.md).
Usage: python report_v3.py EXCHANGE_DIR OUT_DIR"""
import sys, json, pathlib
import numpy as np, pandas as pd
EX = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
HERE = pathlib.Path(__file__).resolve().parent
R = json.load(open(EX / 'views-v3-run-j.json')); VAI = json.loads(str(np.load(EX / 'view-a-i-v3.npz')['meta']))
DK = [f'D{d}' for d in range(6)]
DN = {'D0': "D0' 00:19 data held out (transmission imposed)", 'D1': 'D1 R600 BTO only', 'D2': 'D2 R600 BTO + raw BFO',
      'D3': 'D3 R600 BTO + both BFOs as recorded', 'D4': 'D4 R600 BTO + both BFOs, Holland transient bias added',
      'D5': 'D5 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added'}
PN = {'core': 'satcom + flight + end of flight (core), settled seabed', 'D': 'core + debris drift (finds only, dedicated arc-latitude run)',
      'S': 'core + searched areas (per-cell model V1 central, settled field)', 'P': 'core + Pleiades objects (conditional on H)',
      'DS': 'ALL: core + drift + searched areas', 'DSP': 'all, conditional on H (Pleiades objects are debris)', 'DP': 'core + drift + Pleiades (given H)',
      'SP': 'core + searched areas + Pleiades (given H)', 'AB': 'core + drift with Australian non-recovery, option B (sensitivity)',
      'ABS': 'all with Australian non-recovery, option B (sensitivity)', 'ACS': 'all with Australian non-recovery, option C (setting)',
      'ApopS': 'all with Australian non-recovery, populated coast only (setting)', 'ABSP': 'all with Australian option B, given H',
      'AC': 'core + drift + Australian option C', 'Apop': 'core + drift + Australian populated coast only', 'ABP': 'core + drift + Australian B + Pleiades (given H)',
      'D100': 'core + drift, kernel 100 km (model error doubled)', 'D100S': 'all, drift kernel 100 km', 'DG': 'core + drift, GLORYS12 only',
      'DC': 'core + drift, GlobCurrent only', 'DGS': 'all, GLORYS12 only', 'DCS': 'all, GlobCurrent only'}
SVN = {'S': 'V1 central (rho field 1x)', 'S_V0': 'V0 scalar base (q 0.945 / 0.9, rho 0.05 flat, OI fractions)', 'S_V2': 'V2 pessimistic',
       'S_V3': 'V3 optimistic', 'S_r0': 'V1, rho field 0x', 'S_r5': 'V1, rho field 5x (rho0 0.25)', 'S_r10': 'V1, rho field 10x (rho0 0.5)',
       'S_rflat': 'V1, rho flat (no terrain shape)', 'S_lpdter': 'V1, lower-confidence areas from terrain only',
       'S_oiu': 'V1, OI coverage as uniform fractions 0.889 / 0.7808 (sensitivity row)', 'S_nooi': 'V1 without Ocean Infinity (sensitivity row)'}
for k, v in SVN.items():
    if k != 'S':
        PN[k] = 'core + searched areas, ' + v; PN['D' + k] = 'all, searched areas ' + v
rows = []
for key, Cc in R['cells'].items():
    variant, d, f, ctx = key.split('|'); B = Cc.get('boot', {})
    for p, x in Cc.items():
        if not isinstance(x, dict) or 'median' not in x:
            continue
        b = B.get(p, {}) if not p.startswith('a_') else {}
        rows.append({'variant': variant, 'option': d, 'family': f, 'context': ctx, 'product': p, 'product_name': PN.get(p, p),
                     'median_lat': x['median'], 'median_se': b.get('median_se'), 'q05': x['q05'], 'q95': x['q95'], 'median_arc_nm': x['median_arc_nm'],
                     'hpd50_km2': x['hpd50_km2'], 'hpd50_se': b.get('hpd50_se'), 'hpd90_km2': x['hpd90_km2'], 'hpd90_se': b.get('hpd90_se'),
                     'hpd95_km2': x['hpd95_km2'], 'hpd95_se': b.get('hpd95_se'), 'hpd99_km2': x['hpd99_km2'],
                     'north_of_33S': x['north_of_33S'], 'north_of_33S_se': b.get('north33_se'), 'kish_ess_north_of_33S': x['kish_ess_north_of_33S'],
                     'eff_sample_north_of_33S_seed_scatter': (b.get('implied_n_north_of_33S') * x['north_of_33S']) if b.get('implied_n_north_of_33S') else None, 'kish_ess': x['kish_ess'], 'n_outcomes': x['n_outcomes_distinct'],
                     'p_on_searched_ground': x['p_on_searched_ground'], 'p_on_searched_ground_se': b.get('searched_se'),
                     'p_in_next_oi_area_not_evidence': x['p_in_next_oi_area_not_evidence'], 'lnE_given_core': x.get('lnE_given_core'),
                     'lnER_core_vs_uniform': x.get('lnER_core_vs_uniform'), 'arc_uniform_unreachable_share': x.get('arc_uniform_unreachable_share'),
                     'waypoints_share': x['stratum_share'].get('run-j-waypoints'), 'A1_share': x['family_share']['A1'], 'A2_share': x['family_share']['A2'],
                     'B_share': x['family_share']['B'], 'n_modes': len(x['modes']), 'modes': '; '.join(f"{m['peak_lat']:.2f} ({m['mass']:.3f})" for m in x['modes'])})
P = pd.DataFrame(rows); P['label_n_north_of_33S'] = P[['eff_sample_north_of_33S_seed_scatter', 'kish_ess_north_of_33S']].min(axis=1); P.to_csv(OUT / 'products-v3.csv', index=False)
H = P[(P.variant == 'head') & (P.family == 'all') & (P.context == 'mix')].set_index(['option', 'product'])

def f1(v, se=None, nd=2, sc=1.0):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '–'
    s = f'{v * sc:.{nd}f}'
    return s + (f' ± {se * sc:.{nd}f}' if se is not None and not (isinstance(se, float) and np.isnan(se)) else '')

md = []
md.append('### Table 1. Headline per 00:19 treatment: core, all evidence, all given H, all with the Australian term (four-stratum mixture, settled seabed)\n')
md.append('| 00:19 treatment | product | median lat (± seed SE) | 50 / 90 / 95 % HPD, thousand km² (90 % ± SE) | mass N of 33 S (± SE) | Kish ESS N of 33 S (outcomes) / effective sample N of 33 S from seed scatter, p²(1−p)/SE² | on searched ground (± SE) | in planned next OI area (not evidence) | Kish ESS |')
md.append('|---|---|---|---|---|---|---|---|---|')
for d in DK:
    for p in ('core', 'DS', 'DSP', 'ABS'):
        x = H.loc[(d, p)]
        md.append(f"| {DN[d]} | {PN[p]} | {f1(x.median_lat, x.median_se)} | {x.hpd50_km2/1e3:.0f} / {x.hpd90_km2/1e3:.0f} ± {0 if pd.isna(x.hpd90_se) else x.hpd90_se/1e3:.0f} / {x.hpd95_km2/1e3:.0f} | "
                  f"{f1(x.north_of_33S, x.north_of_33S_se, 3)} | {x.kish_ess_north_of_33S:.0f} / {0 if pd.isna(x.eff_sample_north_of_33S_seed_scatter) else x.eff_sample_north_of_33S_seed_scatter:.0f} | "
                  f"{f1(x.p_on_searched_ground, x.p_on_searched_ground_se, 3)} | {x.p_in_next_oi_area_not_evidence:.4f} | {x.kish_ess:.0f} |")
# Table 2 waypoints vs free flight
md.append('\n### Table 2. Waypoints against free flight (each CONDITIONAL on its stratum), settled seabed\n')
md.append('| 00:19 treatment | stratum | core median / 90 % area (k km²) / N of 33 S | all evidence median / 90 % area / N of 33 S / on searched ground | Kish ESS all | stratum share in the mixture, core → all |')
md.append('|---|---|---|---|---|---|')
for d in DK:
    for s in ('run-j-waypoints', 'run-j-free', 'run-j-descent-climb', 'run-j-repro-radar'):
        q = P[(P.variant == 'head') & (P.family == 'all') & (P.context == s) & (P.option == d)].set_index('product')
        if q.empty:
            continue
        c, a = q.loc['core'], q.loc['DS']; sc = H.loc[(d, 'core')]; sa = H.loc[(d, 'DS')]
        shc = R['cells'][f'head|{d}|all|mix']['core']['stratum_share'].get(s, 0); sha = R['cells'][f'head|{d}|all|mix']['DS']['stratum_share'].get(s, 0)
        md.append(f"| {DN[d]} | {s.replace('run-j-', '')} | {c.median_lat:.2f} / {c.hpd90_km2/1e3:.0f} / {c.north_of_33S:.3f} | {a.median_lat:.2f} / {a.hpd90_km2/1e3:.0f} / {a.north_of_33S:.3f} / {a.p_on_searched_ground:.3f} | {a.kish_ess:.0f} | {shc:.4f} → {sha:.4f} |")
# Table 3 families
md.append('\n### Table 3. Per flight-end family (A1 = cruise to fuel exhaustion then no control; A2 = cruise to fuel exhaustion then controlled descent; B = planned descent with ditching approach begun before fuel exhaustion), four-stratum mixture of the family products\n')
md.append('| 00:19 treatment | family | share core → all | all evidence median / 90 % area (k km²) / N of 33 S / on searched ground | Kish ESS all (core) | settling row ESS of the waypoints product | gate |')
md.append('|---|---|---|---|---|---|---|')
a1ready = any((EX.parent / 'searched-areas').glob('run-j-a1branch*/READY'))
for d in DK:
    for f in ('A1', 'A2', 'B'):
        q = P[(P.variant == 'head') & (P.family == f) & (P.context == 'mix') & (P.option == d)].set_index('product')
        if q.empty:
            continue
        c, a = q.loc['core'], q.loc['DS']
        shc = H.loc[(d, 'core')][f + '_share']; sha = H.loc[(d, 'DS')][f + '_share']
        blk = R['cells'][f'head|{d}|{f}|mix']['blocks']; wp = [b for b in blk if b['s'] == 'run-j-waypoints'][0]
        gate = 'below the gate (row ESS < 500); A1-branch stratum not landed' if (wp['row_ess'] < 500) else ('below 1,000' if wp['row_ess'] < 1000 else 'pass')
        md.append(f"| {DN[d]} | {f} | {shc:.3f} → {sha:.3f} | {a.median_lat:.2f} / {a.hpd90_km2/1e3:.0f} / {a.north_of_33S:.3f} / {a.p_on_searched_ground:.3f} | {a.kish_ess:.0f} ({c.kish_ess:.0f}) | {wp['row_ess']:.0f} ({wp['fs'].replace('run-j-', '')}) | {gate} |")
# Table 4 sensitivities
md.append('\n### Table 4. Sensitivity of ALL evidence (core + drift + searched areas) to the search-model level and to other inputs, per 00:19 treatment (median lat / 90 % area k km² / N of 33 S / on searched ground)\n')
SENS = ['DS', 'DS_r0', 'DS_r5', 'DS_r10', 'DS_V0', 'DS_V2', 'DS_V3', 'DS_rflat', 'DS_lpdter', 'DS_oiu', 'DS_nooi', 'D100S', 'DGS', 'DCS', 'ABS', 'ACS', 'ApopS']
SL = {'DS': 'base: V1 central, rho field 1x', 'DS_r0': 'rho field 0x', 'DS_r5': 'rho field 5x', 'DS_r10': 'rho field 10x', 'DS_V0': 'q level V0 (scalar)',
      'DS_V2': 'q level V2 (pessimistic)', 'DS_V3': 'q level V3 (optimistic)', 'DS_rflat': 'rho flat', 'DS_lpdter': 'lower-confidence from terrain',
      'DS_oiu': 'OI coverage fractions (sensitivity row)', 'DS_nooi': 'without OI (sensitivity row)', 'D100S': 'drift kernel 100 km', 'DGS': 'GLORYS12 only',
      'DCS': 'GlobCurrent only', 'ABS': 'Australian option B (sens.)', 'ACS': 'Australian option C (setting)', 'ApopS': 'Australian populated only (setting)'}
md.append('| setting | ' + ' | '.join(d for d in DK) + ' |'); md.append('|---|' + '---|' * len(DK))
srows = []
for p in SENS:
    cells = []
    for d in DK:
        x = H.loc[(d, p)]; cells.append(f"{x.median_lat:.2f} / {x.hpd90_km2/1e3:.0f} / {x.north_of_33S:.3f} / {x.p_on_searched_ground:.3f}")
        srows.append({'setting': SL[p], 'product': p, 'option': d, 'median_lat': x.median_lat, 'median_se': x.median_se, 'hpd90_km2': x.hpd90_km2, 'hpd90_se': x.hpd90_se,
                      'north_of_33S': x.north_of_33S, 'north_of_33S_se': x.north_of_33S_se, 'p_on_searched_ground': x.p_on_searched_ground, 'p_on_searched_ground_se': x.p_on_searched_ground_se,
                      'kish_ess': x.kish_ess})
    md.append(f'| {SL[p]} | ' + ' | '.join(cells) + ' |')
pd.DataFrame(srows).to_csv(OUT / 'sensitivity-v3.csv', index=False)
# Table 5 influence
md.append('\n### Table 5. Influence by factor (KL divergence, nats, with seed-bootstrap SE); leave-one-out on ALL and on all given H\n')
md.append('| 00:19 treatment | KL(all ‖ core) | searched areas: KL(all ‖ all without it), share | drift: KL, share | removing searched areas: Δ median (NM), Δ 90 % area (k km²) | removing drift: Δ median (NM), Δ 90 % | given H: Pléiades KL(all|H ‖ all), share of KL(all|H ‖ core) | flags |')
md.append('|---|---|---|---|---|---|---|---|')
irows = []
for d in DK:
    Cc = R['cells'][f'head|{d}|all|mix']; L = Cc['loo']; BK = Cc['boot_KL']
    s_, dr = L['S|DS'], L['D|DS']; pp = L['P|DSP']
    se = lambda k: BK.get(k, {}).get('se', np.nan)
    flags = [n for n, x in (('searched areas', s_), ('drift', dr), ('Pléiades given H', pp)) if x['flag_KL_gt_half']]
    dom = [f"{k} {v:.3f}" for k, v in Cc['DS']['stratum_share'].items() if v > 0.95]
    md.append(f"| {DN[d]} | {s_['KL_all_vs_core']:.3f} ± {se('DS|core'):.3f} | {s_['KL_all_vs_loo']:.3f} ± {se('DS|D'):.3f}, {s_['KL_share_of_total']:.2f} | {dr['KL_all_vs_loo']:.3f} ± {se('DS|S'):.3f}, {dr['KL_share_of_total']:.2f} | "
              f"{s_['median_shift_on_removal_nm']:+.0f}, {s_['hpd90_change_on_removal_km2']/1e3:+.0f} | {dr['median_shift_on_removal_nm']:+.0f}, {dr['hpd90_change_on_removal_km2']/1e3:+.0f} | "
              f"{pp['KL_all_vs_loo']:.3f} ± {se('DSP|DS'):.3f}, {pp['KL_share_of_total']:.2f} | KL > half: {', '.join(flags) or 'none'}; model dominance (> 0.95): {', '.join(dom) or 'none'} |")
    for k, x in L.items():
        irows.append({'option': d, 'factor|product': k, **{kk: vv for kk, vv in x.items()}})
    for k, x in Cc['KL'].items():
        irows.append({'option': d, 'factor|product': 'KL ' + k, 'KL': x, 'KL_se': se(k)})
pd.DataFrame(irows).to_csv(OUT / 'influence-v3.csv', index=False)
# Table 6 view (a)
md.append("\n### Table 6. Each evidence type alone (prior uniform along the 7th arc, 40.6–11.8 S, same end-of-flight model), D0'\n")
md.append('| evidence | (i) sampling-free surface: median lat / N of 33 S | (ii) settled outcome sample reweighted: median lat / N of 33 S / Kish ESS / unreachable share of the arc span | ln evidence ratio core vs uniform (ii) / (i) | 90 % HPD overlap with core: mass of core in (ii) region, Bhattacharyya |')
md.append('|---|---|---|---|---|')
Cc = R['cells']['head|D0|all|mix']
for E, nm in (('D', 'debris drift (finds only)'), ('S', 'searched areas V1 central'), ('S_V0', 'searched areas V0'), ('S_V2', 'searched areas V2'), ('S_V3', 'searched areas V3'),
              ('S_r0', 'searched areas rho 0x'), ('S_r10', 'searched areas rho 10x'), ('P', 'Pléiades (conditional on H)'), ('AB', 'drift + Australian option B (sens.)')):
    a = Cc['a_' + E]; vi = VAI[E]; lnEi = Cc[E]['lnE_given_core'] - vi['lnE_uniform_i']
    md.append(f"| {nm} | {vi['median_lat']:.2f} / {vi['north_of_33S']:.3f} | {a['median']:.2f} / {a['north_of_33S']:.3f} / {a['kish_ess']:.0f} / {a['arc_uniform_unreachable_share']:.3f} | {a['lnER_core_vs_uniform']:+.2f} / {lnEi:+.2f} | {a['vs_core']['mass_a_in_b']:.2f}, {a['vs_core']['bhattacharyya']:.2f} |")
md.append(f"\nUniform base (i): median {VAI['U']['median_lat']:.2f}, N of 33 S {VAI['U']['north_of_33S']:.3f}. Drift (i) not computed share (north of run A grid, 21.2 S; carried at the mean): {VAI['D']['not_computed_share']:.3f}.")
# Pleiades odds
md.append('\n### Table 7. Pléiades: both ways, and the change in the odds of H from the evidence other than the imagery\n')
md.append('| 00:19 treatment | all: median / 90 % (k km²) | all given H: median / 90 % | ln odds factor of H from drift + searches, ln[Z(all|H) Z(core) / (Z(core+P) Z(all))] | P(H | D) for prior P(H) 0.1 / 0.25 / 0.5 (identity likelihood ratio of the imagery taken as 1) |')
md.append('|---|---|---|---|---|')
orows = []
for d in DK:
    Cc = R['cells'][f'head|{d}|all|mix']; k = Cc['DSP']['lnE_given_core'] - Cc['P']['lnE_given_core'] - Cc['DS']['lnE_given_core']
    ph = [p0 * np.exp(k) / (p0 * np.exp(k) + 1 - p0) for p0 in (0.1, 0.25, 0.5)]
    md.append(f"| {DN[d]} | {Cc['DS']['median']:.2f} / {Cc['DS']['hpd90_km2']/1e3:.0f} | {Cc['DSP']['median']:.2f} / {Cc['DSP']['hpd90_km2']/1e3:.0f} | {k:+.2f} | {ph[0]:.3f} / {ph[1]:.3f} / {ph[2]:.3f} |")
    orows.append({'option': d, 'ln_odds_factor_nonimagery': k, 'P_H_given_D_prior0.1': ph[0], 'P_H_given_D_prior0.25': ph[1], 'P_H_given_D_prior0.5': ph[2]})
pd.DataFrame(orows).to_csv(OUT / 'pleiades-odds-v3.csv', index=False)
# Table 8 comparison with v2
V2 = pd.read_csv(HERE.parent / 'composer-views-run-j/products.csv'); V2 = V2[V2.context == 'mix'].set_index(['option', 'product'])
md.append('\n### Table 8. Views v3 (settled seabed, per-cell search model, dedicated drift run) against views v2 (impact point, scalar search model, run A drift)\n')
md.append('| 00:19 treatment | product | v2 median / 90 % (k km²) / N of 33 S / on searched ground | v3 median / 90 % / N of 33 S / on searched ground | Δ median (deg, + = north) |')
md.append('|---|---|---|---|---|')
crows = []
for d in DK:
    for p in ('core', 'D', 'S', 'DS', 'DSP'):
        if (d, p) not in V2.index:
            continue
        a = V2.loc[(d, p)]; b = H.loc[(d, p)]
        md.append(f"| {DN[d]} | {PN[p]} | {a.median_lat:.2f} / {a.hpd90_km2/1e3:.0f} / {a.north_of_33S:.3f} / {a.p_on_searched_ground_incl_OI:.3f} | {b.median_lat:.2f} / {b.hpd90_km2/1e3:.0f} / {b.north_of_33S:.3f} / {b.p_on_searched_ground:.3f} | {b.median_lat - a.median_lat:+.2f} |")
        crows.append({'option': d, 'product': p, 'v2_median': a.median_lat, 'v3_median': b.median_lat, 'v2_hpd90_km2': a.hpd90_km2, 'v3_hpd90_km2': b.hpd90_km2,
                      'v2_north33': a.north_of_33S, 'v3_north33': b.north_of_33S, 'v2_searched': a.p_on_searched_ground_incl_OI, 'v3_searched': b.p_on_searched_ground})
pd.DataFrame(crows).to_csv(OUT / 'compare-v2-v3.csv', index=False)
# checks / not computed
md.append('\n### Checks\n')
for s, c in R['meta']['checks'].items():
    md.append(f"- {s}: outcomes used {c['n_outcomes_used']:,} of {c['n_outcomes_folder']:,}; module Z reproduced, max |Δ| {c['module_Z_max_abs_diff']:.1e}; "
              f"end-of-flight latitude max |Δ| {c['eof_latitude_max_abs_diff']:.1e}; Pléiades cell mismatches {c['pleiades_cell_mismatch'][0]} of {c['pleiades_cell_mismatch'][1]:,}; "
              f"carried outcomes {c['carried_outcomes']}; drift inside the dedicated-run span {c['drift_inside_dedicated_span_share']:.3f} of outcomes")
pc = {}
for d in DK:
    for k, v in R['cells'][f'head|{d}|all|mix']['not_computed_share'].items():
        if k.startswith('drift|off') or k.startswith('pleiades'):
            pc[k] = max(pc.get(k, 0), v)
md.append('- Not-computed share of base weight (max over D, per stratum block): ' + '; '.join(f'{k} {v:.1e}' for k, v in pc.items()))
for d in ('D3', 'D4'):
    a, b = R['cells'][f'head|{d}|all|mix']['DS'], R['cells'][f'prodonly|{d}|all|mix']['DS']
    md.append(f"- {d} waypoints from production instead of both-burst (check): all evidence median {b['median']:.2f} (head {a['median']:.2f}), 90 % {b['hpd90_km2']/1e3:.0f}k (head {a['hpd90_km2']/1e3:.0f}k), N of 33 S {b['north_of_33S']:.3f} (head {a['north_of_33S']:.3f})")
(OUT / 'note-tables-v3.md').write_text('\n'.join(md) + '\n')
print('\n'.join(md))
