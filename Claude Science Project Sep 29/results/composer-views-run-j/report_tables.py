"""Composer views on run J, step 3a: CSV tables and markdown tables from views-run-j.json. Usage: python report_tables.py OUTDIR"""
import sys, json, csv, pathlib, numpy as np
OUT = pathlib.Path(sys.argv[1]); RJ = json.load(open(OUT / 'views-run-j.json'))
DK = [f'D{d}' for d in range(6)]
DNAME = {'D0': '00:19 data held out', 'D1': '00:19:29 BTO', 'D2': '00:19:29 BTO + BFO', 'D3': 'both 00:19 BFOs as recorded',
         'D4': 'both 00:19 BFOs, shared start-up offset', 'D5': '00:19:37 BFO with start-up offset'}
PN = {'core': 'satcom + flight + end of flight (core)', 'D': 'core + debris drift (finds)', 'S': 'core + searched areas',
      'P': 'core + Pleiades objects (conditional on H)', 'A': 'core + drift with Australian non-recovery (sensitivity)',
      'DS': 'ALL (core + drift + searched areas)', 'DP': 'core + drift + Pleiades (conditional on H)', 'SP': 'core + searched areas + Pleiades (conditional on H)',
      'DSP': 'ALL conditional on H (core + drift + searched areas + Pleiades)', 'AS': 'ALL with Australian non-recovery (sensitivity)',
      'AP': 'core + drift with Australian term + Pleiades (conditional, sensitivity)', 'ASP': 'ALL with Australian term, conditional on H (sensitivity)',
      'D100': 'core + drift, kernel 100 km (model error doubled)', 'D100S': 'ALL with drift kernel 100 km (model error doubled)',
      'S10': 'core + searched areas, rho 0.10 (model error doubled)', 'DS10': 'ALL with searched-areas rho 0.10 (model error doubled)',
      'DG': 'core + drift, GLORYS12 only', 'DC': 'core + drift, GlobCurrent only', 'DGS': 'ALL, drift GLORYS12 only', 'DCS': 'ALL, drift GlobCurrent only'}
EN = {'D': 'debris drift (finds)', 'S': 'searched areas', 'P': 'Pleiades objects (conditional on H)', 'A': 'drift with Australian non-recovery (sensitivity)'}
CTX = ['mix', 'A1', 'A2', 'B', 'run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb']
def f(x, n=3):
    return '' if x is None else (f'{x:.{n}f}' if isinstance(x, float) else str(x))
# 1. products per option x context
rows = []
for d in DK:
    for ctx in CTX:
        C = RJ['cells'][f'head|{d}|{ctx}']
        for p, x in [(k, C[k]) for k in PN] + [('a_' + E, C['a_' + E]) for E in ('D', 'S', 'P', 'A', 'D100', 'S10')]:
            b = RJ['boot'][d].get(p, {}) if ctx == 'mix' else {}
            n_impl = b.get('implied_n_north_of_33S'); n33 = None if n_impl is None else n_impl * x['north_of_33S']
            if p.startswith('a_') and ctx == 'mix':
                n33 = n_impl * x['north_of_33S'] if n_impl else None
            kn = x.get('kish_ess_north_of_33S'); label_n = min(v for v in (n33, kn) if v is not None) if (n33 is not None or kn is not None) else None
            rows.append({'option': d, 'option_name': DNAME[d], 'context': ctx, 'product': p,
                         'product_name': PN.get(p, ('E ALONE, prior uniform along the arc (reweighted run J samples): ' + EN.get(p[2:], p[2:])) if p.startswith('a_') else p),
                         'median_lat': x['median'], 'median_se': b.get('median_se'), 'q05': x['q05'], 'q95': x['q95'], 'mean_lat': x['mean'],
                         'hpd50_km2': x['hpd50_km2'], 'hpd90_km2': x['hpd90_km2'], 'hpd95_km2': x['hpd95_km2'],
                         'north_of_33S': x['north_of_33S'], 'north_of_33S_se': b.get('north33_se'), 'eff_sample_north_of_33S_seed_scatter': n33, 'kish_ess_north_of_33S': kn, 'label_n_north_of_33S': label_n,
                         'north_of_30S': x['north_of_30S'], 'ESS_kish': x['ESS'], 'p_on_searched_ground': x.get('p_on_searched_ground'),
                         'lnE_given_core': x.get('lnE_given_core'), 'KL_vs_core': (x.get('KL') or {}).get('core'),
                         'waypoints_share': (x.get('stratum_share') or {}).get('run-j-waypoints'),
                         'A1_share': (x.get('family_share') or {}).get('A1'), 'A2_share': (x.get('family_share') or {}).get('A2'), 'B_share': (x.get('family_share') or {}).get('B'),
                         'n_modes': len(x['modes']), 'uniform_share_unreachable': x.get('uniform_share_unreachable')})
with open(OUT / 'products.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
# 2. bands per option (mixture), with seed-bootstrap SE
BE = np.arange(-50, -5, 1.0)
with open(OUT / 'bands-1deg-mixture.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['option', 'product', 'band_south_edge', 'band_north_edge', 'mass', 'mc_se_seed_bootstrap', 'mass_on_searched_ground'])
    for d in DK:
        C = RJ['cells'][f'head|{d}|mix']
        for p in list(PN) + ['a_D', 'a_S', 'a_P', 'a_A']:
            x = C[p]; se = RJ['boot'][d].get(p, {}).get('band_se'); sb = x.get('searched_by_band')
            for i, a in enumerate(BE[:-1]):
                w.writerow([d, p, a, a + 1, f'{x["bands"][i]:.6g}', '' if se is None else f'{se[i]:.3g}', '' if sb is None else f'{sb[i]:.6g}'])
# 3. modes
with open(OUT / 'modes.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['option', 'context', 'product', 'peak_lat', 'mass', 'from_lat', 'to_lat'])
    for d in DK:
        for ctx in ('mix', 'A1', 'A2', 'B'):
            C = RJ['cells'][f'head|{d}|{ctx}']
            for p in list(PN) + ['a_D', 'a_S', 'a_P', 'a_A']:
                for m in C[p]['modes']:
                    w.writerow([d, ctx, p, f'{m["peak_lat"]:.2f}', f'{m["mass"]:.4f}', f'{m["from_lat"]:.2f}', f'{m["to_lat"]:.2f}'])
# 4. disagreement and influence
dis = []
for d in DK:
    for ctx in CTX:
        C = RJ['cells'][f'head|{d}|{ctx}']
        for E in ('D', 'S', 'P', 'A', 'D100', 'S10'):
            a = C['a_' + E]; v = a['vs_core']
            dis.append({'option': d, 'context': ctx, 'evidence': E, 'comparison': '(a) E alone vs core',
                        'conditioning': 'ln E_core[L_E] - ln E_U[L_E]; U = uniform along the arc (span of run J impacts) with the core cross-arc impact spread per row; impact-point likelihoods',
                        'ln_evidence_ratio': a['lnER_core_vs_uniform'], 'ln_evidence_ratio_view_i': a.get('lnER_core_vs_uniform_i'),
                        'mass_core_in_E90': v['mass_a_in_b'], 'mass_E_in_core90': v['mass_b_in_a'], 'area_core90_in_E90': v['area_a_in_b'], 'area_E90_in_core90': v['area_b_in_a'],
                        'bhattacharyya': v['bhattacharyya'], 'median_shift_deg': v['median_shift_deg'], 'median_shift_nm_along_arc': v['median_shift_nm']})
        for k, v in C['loo'].items():
            E, allp = k.split('|')
            dis.append({'option': d, 'context': ctx, 'evidence': E, 'comparison': f'(c) all except E vs all [{allp}]',
                        'conditioning': f'ln E_(all except E)[L_E] = ln Z({allp}) - ln Z({v["leave_out_product"]}); second value minus ln E_U[L_E]',
                        'ln_evidence_ratio': v['lnE_E_given_others'], 'ln_evidence_ratio_view_i': v['lnER_vs_uniform'],
                        'mass_core_in_E90': v['mass_a_in_b'], 'mass_E_in_core90': v['mass_b_in_a'], 'area_core90_in_E90': v['area_a_in_b'], 'area_E90_in_core90': v['area_b_in_a'],
                        'bhattacharyya': v['bhattacharyya'], 'median_shift_deg': v['median_shift_on_removal_deg'], 'median_shift_nm_along_arc': v['median_shift_on_removal_nm'],
                        'KL_all_vs_all_except_E': v['KL_all_vs_loo'], 'KL_all_vs_core': v['KL_all_vs_core'], 'KL_share': v['KL_share_of_total'],
                        'flag_KL_gt_half': v['flag_KL_gt_half'], 'hpd90_change_on_removal_km2': v['hpd90_change_on_removal_km2']})
keys = sorted({k for r in dis for k in r}, key=lambda k: list(dis[-1]).index(k) if k in dis[-1] else 99)
with open(OUT / 'disagreement-influence.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(dis)
# 5. coverage: ESS and effective sample per 5 deg band (mixture), not-computed shares
with open(OUT / 'coverage-ess.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['option', 'product', 'band_5deg_south_edge', 'mass', 'kish_ess_within_band', 'implied_n_total_from_seed_scatter', 'effective_sample_in_band'])
    for d in DK:
        C = RJ['cells'][f'head|{d}|mix']
        for p in ['core', 'D', 'S', 'P', 'A', 'DS', 'DSP', 'AS', 'ASP', 'a_D', 'a_S', 'a_P', 'a_A']:
            x = C[p]; b = RJ['boot'][d].get(p, {})
            for lo in range(-50, -5, 5):
                m = float(sum(x['bands'][i] for i, a in enumerate(BE[:-1]) if lo <= a < lo + 5)); ni = (b.get('implied_n_by_5deg') or {}).get(str(lo))
                w.writerow([d, p, lo, f'{m:.4g}', f'{x["kish_ess_by_5deg"].get(str(lo), 0):.4g}', '' if ni is None else f'{ni:.4g}', '' if ni is None else f'{ni * m:.4g}'])
with open(OUT / 'not-computed.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['variant', 'option', 'factor_column', 'share_of_core_weight_not_computed'])
    for k, v in sorted(RJ['not_computed'].items()):
        w.writerow(k.split('|') + [f'{v:.3g}'])
print('tables written', len(rows), len(dis))
